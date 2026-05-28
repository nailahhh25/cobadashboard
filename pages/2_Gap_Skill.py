# pages/2_Gap_Skill.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.style  import (inject_css, page_header, section, insight, warn,
                           dl_csv, PALETTE, lyt)
from utils.loader import (skill_gap, kamus_skill, hard_skills, taxonomy,
                           gap_domain, sertifikasi_demand, catalog, explode_pipe, jd)

st.set_page_config(page_title="Gap Skill · Evalify",
                   page_icon="🔍", layout="wide")
inject_css()

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 8px;'>
    <span style='font-size:2rem;'>⚡</span><br>
    <b style='color:#E0E7FF;font-size:1rem;'>Evalify</b></div>""",
    unsafe_allow_html=True)
    st.markdown("<hr style='border-color:rgba(255,255,255,0.1);'>",
                unsafe_allow_html=True)
    st.markdown("""<div style='font-size:0.78rem;color:#A5B4FC;'>
    🔍 <b style='color:#C7D2FE;'>Halaman ini membahas:</b><br><br>
    • Skill apa yang paling langka di pasar<br>
    • Skill yang justru sudah terlalu banyak<br>
    • Domain keahlian yang paling dibutuhkan<br>
    • Tools/teknologi yang kurang dimiliki kandidat<br>
    • Sertifikasi paling bernilai di mata perusahaan
    </div>""", unsafe_allow_html=True)

with st.spinner("Memuat analisis skill…"):
    df_gap  = skill_gap()
    df_ksd  = kamus_skill()
    hs      = hard_skills()
    tax     = taxonomy()
    df_dom  = gap_domain()
    df_cert = sertifikasi_demand()
    df_cat  = catalog()

df_gap["Tipe"] = df_gap["skill"].apply(
    lambda s: "Hard Skill" if str(s).lower() in hs else "Soft Skill")

page_header("Analisis Gap Skill",
            "Temukan skill apa yang paling langka, apa yang sudah berlebih, "
            "dan di mana peluang terbaik untuk meningkatkan nilai jual kamu.", "🔍")

# KPI
shortage = (df_gap["gap_score"] > 0).sum()
surplus  = (df_gap["gap_score"] < 0).sum()
top_miss = df_gap.sort_values("gap_score", ascending=False).iloc[0]["skill"] if len(df_gap) else "—"

c1,c2,c3,c4 = st.columns(4)
c1.metric("Skill yang Dianalisis", f"{len(df_gap):,}")
c2.metric("Skill yang Kurang di Pasar 🔴", f"{shortage:,}",
          help="Banyak dicari tapi sedikit yang punya")
c3.metric("Skill yang Sudah Banyak 🔵", f"{surplus:,}",
          help="Banyak yang punya tapi permintaan rendah")
c4.metric("Skill Paling Langka Saat Ini", str(top_miss).title()[:22])
st.markdown("<hr>", unsafe_allow_html=True)

# ═══ SECTION 1: Supply vs Demand ══════════════════════════════════
section("📊 Skill yang Paling Dicari vs yang Dimiliki Kandidat")

with st.container(border=True):
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        top_n  = st.slider("Tampilkan berapa skill?", 10, 50, 20, key="g1_n")
    with c_f2:
        urutan = st.radio("Urutkan berdasarkan",
                          ["Paling Banyak Dicari","Paling Banyak Dimiliki","Selisih Terbesar"],
                          key="g1_sort")
    with c_f3:
        tipe   = st.radio("Tipe skill", ["Semua","Hard Skill","Soft Skill"], key="g1_t")

    scol = {"Paling Banyak Dicari":"demand_pct",
            "Paling Banyak Dimiliki":"candidate_pct",
            "Selisih Terbesar":"gap_score"}[urutan]
    df_f = df_gap.copy()
    if tipe != "Semua": df_f = df_f[df_f["Tipe"]==tipe]
    df_f = df_f.sort_values(scol, ascending=False).head(top_n)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Dibutuhkan Industri",
                         x=df_f["skill"], y=df_f["demand_pct"]*100,
                         marker_color="#F59E0B",
                         hovertemplate="<b>%{x}</b><br>Dibutuhkan: %{y:.2f}%<extra></extra>"))
    fig.add_trace(go.Bar(name="Dimiliki Kandidat",
                         x=df_f["skill"], y=df_f["candidate_pct"]*100,
                         marker_color="#4F46E5",
                         hovertemplate="<b>%{x}</b><br>Dimiliki: %{y:.2f}%<extra></extra>"))
    fig.update_layout(**lyt(barmode="group", xaxis_tickangle=-40,
                             yaxis_title="Persentase (%)",
                             title="Perbandingan: Skill yang Dibutuhkan vs yang Dimiliki"))
    st.plotly_chart(fig, use_container_width=True)
    dl_csv(df_f[["skill","demand_pct","candidate_pct","gap_score"]], "skill_supply_demand.csv")

insight("Kolom kuning tinggi tapi biru rendah = skill yang langka dan bernilai tinggi "
        "— inilah skill yang perlu kamu kuasai untuk lebih kompetitif.")

# ═══ SECTION 2: Shortage & Surplus ════════════════════════════════
st.markdown("<hr>", unsafe_allow_html=True)
section("📉 Skill yang Langka vs yang Sudah Berlebih di Pasar")

with st.container(border=True):
    c_f4, c_f5, c_f6 = st.columns(3)
    with c_f4:
        tampil = st.radio("Tampilkan", ["Keduanya","Yang Langka","Yang Berlebih"],
                          key="g2_show")
    with c_f5:
        min_gap = st.slider("Minimal selisih", 0.0, 0.5, 0.05, step=0.01, key="g2_mg")
    with c_f6:
        min_dem = st.slider("Minimal permintaan industri", 0, 500, 50, key="g2_md")

    df_g = df_gap[(df_gap["gap_score"].abs() >= min_gap) &
                  (df_gap["demand_count"] >= min_dem)].copy()
    if tampil == "Yang Langka":    df_g = df_g[df_g["gap_score"] > 0]
    elif tampil == "Yang Berlebih": df_g = df_g[df_g["gap_score"] < 0]
    df_g = df_g.sort_values("gap_score", ascending=False).head(40)
    df_g["warna_label"] = df_g["gap_score"].apply(
        lambda v: "🔴 Langka" if v > 0 else "🔵 Berlebih")

    fig2 = px.bar(df_g, x="gap_score", y="skill", orientation="h",
                  color="gap_score",
                  color_continuous_scale=[[0,"#4F46E5"],[0.5,"#F3F4F6"],[1,"#EF4444"]],
                  hover_data={"demand_count":True,"candidate_count":True},
                  labels={"gap_score":"Selisih (+ = Langka, − = Berlebih)",
                          "skill":"",
                          "demand_count":"Permintaan",
                          "candidate_count":"Jumlah yang Punya"},
                  title="Peta Kelangkaan Skill: Merah = Langka, Biru = Berlebih")
    fig2.add_vline(x=0, line_dash="dash", line_color="#9CA3AF")
    fig2.update_layout(**lyt(coloraxis_showscale=False))
    fig2.update_yaxes(autorange="reversed")
    st.plotly_chart(fig2, use_container_width=True)
    dl_csv(df_g[["skill","demand_count","candidate_count","gap_score"]], "skill_langka_berlebih.csv")

# ═══ SECTION 3: Bubble Matrix ══════════════════════════════════════
st.markdown("<hr>", unsafe_allow_html=True)
section("🎯 Peta Persaingan Skill — Kuadran Hot Skills")

st.caption("**Hot Skills** = pojok kanan bawah (banyak dicari, sedikit yang punya). "
           "Inilah skill yang paling bernilai di pasar saat ini.")

with st.container(border=True):
    c_b1, c_b2 = st.columns([3,1])
    with c_b2:
        min_d = st.slider("Min. permintaan", 0, 1000, 100, key="g3_md")
        label_on = st.checkbox("Tampilkan nama skill", key="g3_lbl")
    with c_b1:
        df_b = df_gap[df_gap["demand_count"] >= min_d].copy()
        df_b["Status"] = df_b["gap_score"].apply(
            lambda v: "Langka (Peluang!)" if v > 0 else "Sudah Banyak")
        fig3 = px.scatter(df_b,
                          x="demand_count", y="candidate_count",
                          size=df_b["gap_score"].abs().clip(lower=0.01),
                          color="Status",
                          color_discrete_map={"Langka (Peluang!)":"#EF4444",
                                              "Sudah Banyak":"#4F46E5"},
                          hover_name="skill",
                          hover_data={"demand_count":":.0f","candidate_count":":.0f",
                                      "gap_score":":.3f","Status":False},
                          size_max=40,
                          labels={"demand_count":"Dicari Industri",
                                  "candidate_count":"Dimiliki Kandidat"},
                          title="Bubble = Besar → Selisih Makin Besar")
        if label_on:
            fig3.update_traces(text=df_b["skill"], textposition="top center",
                               textfont=dict(size=9))
        mv = max(df_b["demand_count"].max(), df_b["candidate_count"].max()) * 1.05
        fig3.add_shape(type="line", x0=0, y0=0, x1=mv, y1=mv,
                       line=dict(dash="dash", color="#D1D5DB", width=1))
        fig3.add_annotation(x=mv*0.6, y=mv*0.72, text="Seimbang",
                            font=dict(color="#9CA3AF", size=11), showarrow=False)
        fig3.update_layout(**lyt())
        st.plotly_chart(fig3, use_container_width=True)

# ═══ SECTION 4: Tools & Domain Gap ════════════════════════════════
st.markdown("<hr>", unsafe_allow_html=True)
section("🔧 Tools & Domain Keahlian yang Paling Kurang")

col_td1, col_td2 = st.columns(2, gap="large")

with col_td1:
    with st.container(border=True):
        st.markdown("**Tools/Teknologi yang Paling Kurang Dimiliki Kandidat**")
        if df_cat is None:
            warn("Membutuhkan file job catalog dari repo AI. "
                 "Jalankan <code>git lfs pull</code> dulu.")
        else:
            tools_dm = explode_pipe(df_cat,"job_required_tools").value_counts().reset_index()
            tools_dm.columns = ["Tools","Permintaan"]
            df_ksd2 = df_ksd.copy(); df_ksd2.columns = ["Tools","Dimiliki"]
            df_ksd2["Tools"] = df_ksd2["Tools"].str.lower()
            tools_dm["Tools_l"] = tools_dm["Tools"].str.lower()
            merged = tools_dm.merge(df_ksd2, left_on="Tools_l", right_on="Tools",
                                    how="left", suffixes=("","_s"))
            merged["Dimiliki"] = merged["Dimiliki"].fillna(0)
            merged["Selisih"]  = merged["Permintaan"] - merged["Dimiliki"]
            tg_n = st.slider("Tampilkan", 10, 30, 15, key="g4_tg")
            show_tg = st.radio("Filter", ["Keduanya","Yang Kurang","Yang Lebih"],
                               horizontal=True, key="g4_show")
            df_tg = merged.sort_values("Selisih", ascending=False)
            if show_tg == "Yang Kurang":   df_tg = df_tg[df_tg["Selisih"]>0]
            elif show_tg == "Yang Lebih":  df_tg = df_tg[df_tg["Selisih"]<0]
            df_tg = df_tg.head(tg_n)
            fig4 = px.bar(df_tg, x="Selisih", y="Tools", orientation="h",
                          color="Selisih",
                          color_continuous_scale=[[0,"#4F46E5"],[0.5,"#F3F4F6"],[1,"#EF4444"]],
                          title="Gap Tools: Merah = Kurang, Biru = Lebih",
                          labels={"Tools":"","Selisih":"Selisih"})
            fig4.add_vline(x=0, line_dash="dash", line_color="#9CA3AF")
            fig4.update_layout(**lyt(coloraxis_showscale=False))
            fig4.update_yaxes(autorange="reversed")
            st.plotly_chart(fig4, use_container_width=True)
            dl_csv(df_tg[["Tools","Permintaan","Dimiliki","Selisih"]], "gap_tools.csv")

with col_td2:
    with st.container(border=True):
        st.markdown("**Domain Keahlian Mana yang Paling Dibutuhkan?**")
        st.caption("Domain = bidang spesialisasi (AI/ML, Cloud, Cybersecurity, dll)")
        dom_show = st.radio("Filter", ["Semua","Yang Kurang","Yang Lebih"],
                            horizontal=True, key="g4_dshow")
        df_dg = df_dom.copy()
        if dom_show == "Yang Kurang":  df_dg = df_dg[df_dg["Selisih"]>0]
        elif dom_show == "Yang Lebih": df_dg = df_dg[df_dg["Selisih"]<0]
        df_dg = df_dg.head(25)
        fig5 = px.bar(df_dg, x="Selisih", y="Domain", orientation="h",
                      color="Selisih",
                      color_continuous_scale=[[0,"#4F46E5"],[0.5,"#F3F4F6"],[1,"#EF4444"]],
                      hover_data={"Dibutuhkan Industri":True,"Dimiliki Kandidat":True},
                      title="Gap Domain Keahlian",
                      labels={"Domain":""})
        fig5.add_vline(x=0, line_dash="dash", line_color="#9CA3AF")
        fig5.update_layout(**lyt(coloraxis_showscale=False))
        fig5.update_yaxes(autorange="reversed")
        st.plotly_chart(fig5, use_container_width=True)
        dl_csv(df_dg, "gap_domain.csv")

insight("Domain seperti AI/ML, Cloud Computing, dan Cybersecurity paling banyak "
        "dibutuhkan tapi paling jarang dimiliki kandidat — peluang besar untuk "
        "spesialisasi!")

# ═══ SECTION 5: Sertifikasi ═══════════════════════════════════════
st.markdown("<hr>", unsafe_allow_html=True)
section("🏆 Sertifikasi yang Paling Dihargai Perusahaan")

with st.container(border=True):
    c_cert1, c_cert2 = st.columns([2,1])
    with c_cert2:
        n_cert = st.slider("Tampilkan", 10, 30, 15, key="g5_n")
        filt_c = st.radio("Filter", ["Semua","Sudah Dimiliki","Belum Dimiliki"],
                          key="g5_f")
    with c_cert1:
        df_c = df_cert.copy()
        if filt_c == "Sudah Dimiliki":  df_c = df_c[df_c["Dimiliki Kandidat"]>0]
        elif filt_c == "Belum Dimiliki": df_c = df_c[df_c["Dimiliki Kandidat"]==0]
        df_c = df_c.head(n_cert)
        fig6 = px.bar(df_c, x="Dicari Industri", y="Sertifikasi",
                      orientation="h", color="Dimiliki Kandidat",
                      color_continuous_scale="Blues",
                      title=f"Top {n_cert} Sertifikasi (Warna = Berapa Kandidat yang Sudah Punya)",
                      labels={"Sertifikasi":"","Dicari Industri":"Frekuensi di Lowongan",
                              "Dimiliki Kandidat":"Kandidat yang Punya"})
        fig6.update_layout(**lyt())
        fig6.update_yaxes(autorange="reversed")
        st.plotly_chart(fig6, use_container_width=True)
        dl_csv(df_c, "sertifikasi_bernilai.csv")

insight("Sertifikasi seperti AWS, Google Cloud, dan PMP sangat jarang dimiliki kandidat "
        "tapi sering muncul di deskripsi pekerjaan — investasi yang sangat worthwhile!")
