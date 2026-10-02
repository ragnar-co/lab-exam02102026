"""Streamlit dashboard. Reads published DuckDB marts only; no metric formulas here."""
import hashlib
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import altair as alt  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

import os  # noqa: E402

from src.cpd import ai_brief, config, i18n, metrics, publish  # noqa: E402
from src.cpd.i18n import label, localize_df, t  # noqa: E402
from src.cpd.viz_theme import COLOR_PALETTE, FONT_RULES, build_css  # noqa: E402

ALL = "all"


def mask(df: pd.DataFrame) -> pd.DataFrame:
    """Display-level pseudonymisation (PDPA boundary) when CPD_MASK_IDENTIFIERS is on."""
    if df is None or not config.mask_identifiers():
        return df
    df = df.copy()
    for col in ("case_id", "owner"):
        if col in df:
            df[col] = df[col].map(lambda v: "id-" + hashlib.sha256(str(v).encode()).hexdigest()[:8])
    return df


def fmt_rate(v) -> str:
    return "n/a" if v is None or pd.isna(v) else f"{v:.1%}"


def col_config(lang: str, df: pd.DataFrame, days_max: int | None = None) -> dict:
    """Display-only column labels (+ date format); dataframe column names stay internal."""
    cfg = {}
    for col in df.columns:
        key = i18n.COLUMN_KEYS.get(col)
        if not key:
            continue
        text = t(lang, key)
        if col == "metric_days_in_current_stage" and days_max is not None:
            cfg[col] = st.column_config.ProgressColumn(text, help=t(lang, "col_days_help"), format="%d", min_value=0, max_value=max(days_max, 1))
        elif col == "stage_entered_date":
            cfg[col] = st.column_config.DateColumn(text, format="YYYY-MM-DD")
        else:
            cfg[col] = st.column_config.Column(text)
    return cfg


def render_header(lang: str, ref_text: str, filter_text: str) -> None:
    st.markdown(
        f"""<div class="cpd-header" role="banner"><p class="cpd-eyebrow">{html.escape(t(lang, 'eyebrow'))}</p>
<h1>{html.escape(t(lang, 'app_title'))}</h1>
<p>{html.escape(t(lang, 'reference_date'))}: <strong>{html.escape(ref_text)}</strong> &nbsp;·&nbsp; {html.escape(t(lang, 'filter'))}:<span class="cpd-pill">{html.escape(filter_text)}</span></p></div>""",
        unsafe_allow_html=True)


def stage_chart(lang: str, by_stage: pd.DataFrame):
    p, f = COLOR_PALETTE, FONT_RULES
    data = by_stage.copy()
    data["stage_label"] = data["stage"].map(lambda v: label(lang, "stage", v))
    count = "metric_open_cases_by_stage"
    base = alt.Chart(data).encode(
        x=alt.X("stage_label:N", sort=None, title=t(lang, "axis_stage"), axis=alt.Axis(labelAngle=0, labelLimit=240, labelFontSize=f["body_size"] + 1, titleFontSize=f["body_size"] + 1)),
        y=alt.Y(f"{count}:Q", title=t(lang, "axis_open"), axis=alt.Axis(labelFontSize=f["body_size"], titleFontSize=f["body_size"] + 1, format=",d")),
        tooltip=[alt.Tooltip("stage_label:N", title=t(lang, "axis_stage")), alt.Tooltip(f"{count}:Q", title=t(lang, "axis_open"), format=",d")])
    bars = base.mark_bar(color=p["primary"], size=56, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    labels = base.mark_text(dy=-8, fontSize=f["body_size"] + 2, fontWeight="bold", color=p["dark"]).encode(text=alt.Text(f"{count}:Q", format=",d"))
    return ((bars + labels).properties(height=320)
            .configure(background=p["white"], font=f["family"]).configure_view(strokeWidth=0)
            .configure_axis(labelColor=p["text"], titleColor=p["text"], gridColor=p["border"], domainColor=p["border"]))


def render_top3(lang: str, top: pd.DataFrame) -> None:
    cols = st.columns(len(top))
    for col, row in zip(cols, top.itertuples(index=False)):
        col.markdown(
            f"""<div class="cpd-rank-card"><span class="cpd-rank-num" aria-label="{html.escape(t(lang, 'col_rank'))} {row.rank}">#{row.rank}</span>
<div class="cpd-days">{html.escape(t(lang, 'days_unit', n=int(row.metric_days_in_current_stage)))}</div>
<div class="cpd-meta">{html.escape(t(lang, 'lbl_case_id'))}: <strong>{html.escape(str(row.case_id))}</strong><br>{html.escape(t(lang, 'lbl_stage'))}: <strong>{html.escape(label(lang, 'stage', row.stage))}</strong><br>{html.escape(t(lang, 'lbl_owner'))}: <strong>{html.escape(str(row.owner))}</strong></div></div>""",
            unsafe_allow_html=True)


def render_ai_section(lang, con, dom, runs) -> None:
    """Optional AI bonus. Any failure here is contained and never affects the core dashboard above."""
    st.subheader(t(lang, "ai_title"))
    try:
        cfg = ai_brief.load_ai_config(os.environ)
        path = ai_brief.store_path(runs)
        st.caption(t(lang, "ai_caption"))
        if not cfg.configured:
            st.info(t(lang, "ai_not_configured", url=ai_brief.ENV_URL, api_key=ai_brief.ENV_KEY))
        if st.button(t(lang, "ai_button"), key="gen_brief", disabled=not cfg.configured):
            with st.spinner(t(lang, "ai_spinner")):
                ai_brief.generate_brief(con, dom, cfg, path)
        latest = ai_brief.latest_brief(path)
        if latest is None:
            st.caption(t(lang, "ai_none"))
            return
        flt = t(lang, "all_cases") if latest["case_domain_filter"] == "all" else label(lang, "case_domain", latest["case_domain_filter"])
        meta = t(lang, "ai_meta", at=latest["generated_at"], run_id=latest["run_id"], flt=flt, ref=latest["reference_date"],
                 model=latest["model_identifier"] or "n/a", bid=latest["brief_id"])
        if latest["generation_status"] == "success":
            st.success(t(lang, "ai_success"))
            st.markdown(latest["brief_text"])
        else:
            st.error(t(lang, "ai_failed", cat=latest["error_category"], msg=latest["error_message"]))
        st.caption(meta)
        if latest["run_id"] != metrics.run_status(con)["run_id"]:
            st.caption(t(lang, "ai_prev_run"))
    except Exception as exc:  # AI section must never break the core dashboard
        st.warning(t(lang, "ai_crash", exc=type(exc).__name__))


def main() -> None:
    lang = st.session_state.get("lang") or i18n.default_lang()
    st.set_page_config(page_title=t(lang, "page_title"), layout="wide")
    st.markdown(build_css(), unsafe_allow_html=True)
    # language switcher: a normal keyed widget, so a switch is a plain rerun that keeps every other widget's state
    with st.container(key="langbar"):
        lang = st.radio(t(lang, "language"), list(i18n.LANGS), index=list(i18n.LANGS).index(lang), key="lang", horizontal=True)
    runs = config.runs_dir()
    last = publish.read_last_report(runs)
    con = publish.connect_published(runs)
    sel = st.session_state.get("case_domain", ALL)
    filter_text = t(lang, "all_cases") if sel == ALL else label(lang, "case_domain", sel)

    if con is None:
        render_header(lang, t(lang, "ref_unavailable"), filter_text)
    if last and last.get("status") != "published":
        st.error(t(lang, "rejected"))
        for i in last.get("issues", []):
            st.write(f"- **[{i['rule']}]** {i['message']} (count: {i['count']})")
    if con is None:
        st.warning(t(lang, "no_run"))
        return

    try:
        status = metrics.run_status(con)
        ref = status["reference_date"]
        ref_text = str(ref) if ref is not None else t(lang, "ref_pending")
        render_header(lang, ref_text, filter_text)
        st.caption(t(lang, "run_info", run_id=status["run_id"], snapshot=status["snapshot_id"], rows=f"{status['row_count']:,}", ref=ref_text))

        kpi_box = st.container(key="kpis")
        with st.container(key="filter"):
            choice = st.selectbox(t(lang, "filter_label"), [ALL] + metrics.case_domains(con), key="case_domain",
                                  format_func=lambda v: t(lang, "all") if v == ALL else label(lang, "case_domain", v),
                                  help=t(lang, "filter_help"))
        dom = None if choice == ALL else choice
        ctx = t(lang, "ctx", label=t(lang, "all") if choice == ALL else label(lang, "case_domain", choice))

        total, closed, open_ = (metrics.scalar(con, n, dom) for n in ("metric_total_cases", "metric_closed_cases", "metric_open_cases"))
        with kpi_box:
            c1, c2, c3 = st.columns(3)
            c1.metric(t(lang, "kpi_total"), f"{int(total):,}", help=t(lang, "kpi_help", metric="metric_total_cases", ctx=ctx))
            c2.metric(t(lang, "kpi_closed"), f"{int(closed):,}", help=t(lang, "kpi_help", metric="metric_closed_cases", ctx=ctx))
            c3.metric(t(lang, "kpi_open"), f"{int(open_):,}", help=t(lang, "kpi_help", metric="metric_open_cases", ctx=ctx))
            st.caption(t(lang, "rates", c=fmt_rate(metrics.scalar(con, "consequence_process_completion_rate", dom)),
                         o=fmt_rate(metrics.scalar(con, "open_case_rate", dom))))

        with st.container(key="stage"):
            st.subheader(t(lang, "stage_title"))
            by_stage = metrics.open_by_stage(con, dom)
            if by_stage.empty:
                st.info(t(lang, "empty"))
            else:
                st.caption(t(lang, "stage_caption", ctx=ctx))
                st.altair_chart(stage_chart(lang, by_stage), width="stretch", theme=None)
                with st.expander(t(lang, "chart_table")):
                    shown = localize_df(by_stage, lang)
                    st.dataframe(shown, hide_index=True, column_config={
                        "stage": st.column_config.Column(t(lang, "col_stage")),
                        "metric_open_cases_by_stage": st.column_config.NumberColumn(t(lang, "axis_open"), format="%d")})

        with st.container(key="drill"):
            st.subheader(t(lang, "drill_title"))
            d1, d2 = st.columns(2)
            d_status = d1.selectbox(t(lang, "status"), [ALL, "open", "closed"], key="drill_status",
                                    format_func=lambda v: t(lang, "all") if v == ALL else label(lang, "case_status", v))
            d_stage = d2.selectbox(t(lang, "stage"), [ALL] + metrics.stages(con), key="drill_stage",
                                   format_func=lambda v: t(lang, "all") if v == ALL else label(lang, "stage", v))
            drill = metrics.case_list(con, dom, None if d_status == ALL else d_status, None if d_stage == ALL else d_stage)
            st.caption(t(lang, "drill_caption", n=f"{len(drill):,}", ctx=ctx))
            st.dataframe(localize_df(mask(drill), lang), hide_index=True, column_config=col_config(lang, drill))

        aging = metrics.case_aging(con, dom)
        top = metrics.top3(con, dom)
        with st.container(key="aging"):
            st.subheader(t(lang, "aging_title"))
            if aging is None:
                reason = status["aging_reason"] or "reference_date not provided"
                st.info(t(lang, "pending_aging", reason=reason))
            else:
                st.caption(t(lang, "aging_caption", ref=ref, n=f"{len(aging):,}", ctx=ctx))
                longest = int(aging["metric_days_in_current_stage"].max()) if len(aging) else 1
                st.dataframe(localize_df(mask(aging), lang), hide_index=True, column_config=col_config(lang, aging, days_max=longest))

        with st.container(key="top3"):
            st.subheader(t(lang, "top3_title"))
            if top is None:
                st.info(t(lang, "pending_top3"))
            elif top.empty:
                st.info(t(lang, "empty"))
            else:
                top = top.copy()
                top.insert(0, "rank", range(1, len(top) + 1))
                shown = mask(top)
                render_top3(lang, shown)
                st.caption(t(lang, "top3_caption"))
                st.dataframe(localize_df(shown, lang), hide_index=True, column_config=col_config(lang, shown), column_order=[
                    "rank", "case_id", "stage", "owner", "metric_days_in_current_stage", "case_domain", "response_type", "stage_entered_date"])

        with st.expander(t(lang, "dq_title")):
            st.dataframe(con.execute("SELECT rule_id, name, severity, scope, status, failing_rows, detail FROM quality_results ORDER BY rule_id").df(), hide_index=True)

        with st.container(key="ai"):
            render_ai_section(lang, con, dom, runs)
    finally:
        con.close()


main()
