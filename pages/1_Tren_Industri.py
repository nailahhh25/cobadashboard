# pages/1_Tren_Industri.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.style  import (inject_css, page_header, section, insight, warn, dl_csv,
                           PALETTE, lyt, BOBOT_SCORING)
from utils.loader import (jd, postings, posting_industri, skill_domain_linkedin,
                           gaji_per_level, catalog, explode_pipe, hard_skills,
                           top_skills as top_sk_loader)

st.set_page_config(page_title="Tren Industri · Evalify",
                   page_icon="🌐", layout="wide")
inject_css()

# ── Sidebar branding ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 8px;'>
    <span style='font-size:2rem;'>⚡</span><br>
    <b style='color:#E0E7FF;font-size:1rem;'>Evalify</b>
    </div>""", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:rgba(255,255,255,0.1);'>",
                unsafe_allow_html=True)
    st.markdown("""<div style='font-size:0.78rem;color:#A5B4FC;'>
    🌐 <b style='color:#C7D2FE;'>Halaman ini membahas:</b><br><br>
    • Pekerjaan apa yang paling banyak dicari<br>
    • Industri yang paling aktif merekrut<br>
    • Skill & tools yang paling dibutuhkan<br>
    • Tren hiring per bulan<br>
    • Benchmark gaji per level karir
    </div>""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────
with st.spinner("Menyiapkan data…"):
    df_jd   = jd()
    df_post = postings()
    df_ind  = posting_industri()
    df_skd  = skill_domain_linkedin()
    df_sal  = gaji_per_level()
    df_cat  = catalog()
    hs      = hard_skills()
    df_topsk = top_sk_loader()

page_header("Tren Industri & Pekerjaan",
            "Lihat industri mana yang paling banyak membuka lowongan, "
            "skill apa yang paling dicari, dan berapa gaji yang ditawarkan.", "🌐")

# ── KPI cards ─────────────────────────────────────────────────────
total_jd   = len(df_jd)
total_li   = len(df_post)
total_ind  = df_ind["industry_name"].nunique()
skill_flat = df_jd["skills_list"].explode()
total_sk   = skill_flat.nunique()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Total Lowongan Terekam", f"{total_jd+total_li:,}")
c2.metric("Industri yang Terwakili", f"{total_ind:,}")
c3.metric("Jenis Pekerjaan Unik", f"{df_jd['title_clean'].nunique():,}")
c4.metric("Skill Unik Terdeteksi", f"{total_sk:,}")

st.markdown("<hr>", unsafe_allow_html=True)

# ═══ SECTION 1: Pekerjaan & Industri ═════════════════════════════
section("📌 Pekerjaan & Industri yang Paling Banyak Dicari")

col_L, col_R = st.columns(2, gap="large")

with col_L:
    with st.container(border=True):
        st.markdown("**Posisi Pekerjaan Paling Populer**")
        top_n = st.slider("Tampilkan berapa posisi?", 5, 25, 12, key="s1_topn")
        tc = df_jd["title_clean"].value_counts().head(top_n).reset_index()
        tc.columns = ["Posisi Pekerjaan","Jumlah Lowongan"]
        fig = px.bar(tc, x="Jumlah Lowongan", y="Posisi Pekerjaan",
                     orientation="h", color="Jumlah Lowongan",
                     color_continuous_scale="Blues",
                     title=f"Top {top_n} Posisi Pekerjaan Terbanyak")
        fig.update_layout(**lyt(coloraxis_showscale=False))
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
        dl_csv(tc, "posisi_populer.csv")

with col_R:
    with st.container(border=True):
        st.markdown("**Industri yang Paling Banyak Membuka Lowongan**")
        top_i = st.slider("Tampilkan berapa industri?", 5, 30, 15, key="s1_topind")
        ic = df_ind["industry_name"].value_counts().head(top_i).reset_index()
        ic.columns = ["Industri","Jumlah Lowongan"]
        fig2 = px.bar(ic, x="Jumlah Lowongan", y="Industri",
                      orientation="h", color="Jumlah Lowongan",
                      color_continuous_scale="Teal",
                      title=f"Top {top_i} Industri Paling Aktif Merekrut")
        fig2.update_layout(**lyt(coloraxis_showscale=False))
        fig2.update_yaxes(autorange="reversed")
        st.plotly_chart(fig2, use_container_width=True)
        dl_csv(ic, "industri_aktif.csv")

# ── Kategori skill LinkedIn ───────────────────────────────────────
with st.container(border=True):
    st.markdown("**Bidang Keahlian yang Paling Banyak Diminta di LinkedIn** *(35 kategori)*")
    sk_cnt = df_skd["skill_name"].value_counts().reset_index()
    sk_cnt.columns = ["Bidang Keahlian","Jumlah Lowongan"]
    st.caption("Setiap lowongan LinkedIn dikelompokkan ke dalam kategori keahlian. "
               "Ini menunjukkan bidang mana yang paling banyak dibutuhkan.")
    fig3 = px.bar(sk_cnt, x="Jumlah Lowongan", y="Bidang Keahlian",
                  orientation="h", color="Jumlah Lowongan",
                  color_continuous_scale="Purples",
                  title="Kategori Keahlian yang Paling Banyak Diminta")
    fig3.update_layout(**lyt(coloraxis_showscale=False, height=520))
    fig3.update_yaxes(autorange="reversed")
    st.plotly_chart(fig3, use_container_width=True)

insight("Bidang seperti IT, Engineering, dan Sales mendominasi lowongan LinkedIn. "
        "Jika kamu berada di bidang ini, persaingan tinggi — pastikan CV kamu menonjol.")

# ═══ SECTION 2: Tren Waktu ════════════════════════════════════════
st.markdown("<hr>", unsafe_allow_html=True)
section("📈 Seberapa Aktif Perusahaan Membuka Lowongan?")

with st.container(border=True):
    col_opt1, col_opt2 = st.columns([2,1])
    with col_opt1:
        gran = st.radio("Lihat tren per", ["Bulan","Kuartal"],
                        horizontal=True, key="s2_gran")
    with col_opt2:
        pilih_ind = st.selectbox("Filter industri (opsional)",
                                 ["Semua"] + sorted(df_ind["industry_name"].dropna().unique()),
                                 key="s2_ind")

    if pilih_ind != "Semua":
        df_trend = df_ind[df_ind["industry_name"]==pilih_ind].copy()
        trend_data = df_trend.groupby(gran).size().reset_index(name="Jumlah Lowongan")
    else:
        trend_data = df_post.groupby(gran).size().reset_index(name="Jumlah Lowongan")
    trend_data = trend_data.sort_values(gran)

    fig4 = px.line(trend_data, x=gran, y="Jumlah Lowongan",
                   title="Tren Pembukaan Lowongan dari Waktu ke Waktu",
                   markers=True)
    fig4.update_traces(line_color=PALETTE[0], line_width=2.5,
                       marker=dict(size=6, color=PALETTE[0]))
    fig4.update_layout(**lyt())
    fig4.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig4, use_container_width=True)

# ═══ SECTION 3: Skill yang Dibutuhkan ════════════════════════════
st.markdown("<hr>", unsafe_allow_html=True)
section("🛠️ Skill Apa yang Paling Sering Muncul di Deskripsi Pekerjaan?")

col_sk1, col_sk2 = st.columns([2, 1], gap="large")

with col_sk1:
    with st.container(border=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            top_sk_n = st.slider("Tampilkan berapa skill?", 5, 30, 15, key="s3_n")
        with col_f2:
            tipe_sk = st.radio("Tipe skill", ["Semua","Hard Skill","Soft Skill"],
                               key="s3_t")
        sk_flat2 = skill_flat.dropna().value_counts().reset_index()
        sk_flat2.columns = ["skill","Frekuensi"]
        sk_flat2["Tipe"] = sk_flat2["skill"].apply(
            lambda s: "Hard Skill" if str(s).lower() in hs else "Soft Skill")
        if tipe_sk != "Semua":
            sk_flat2 = sk_flat2[sk_flat2["Tipe"]==tipe_sk]
        sk_top = sk_flat2.head(top_sk_n)
        fig5 = px.bar(sk_top, x="Frekuensi", y="skill",
                      orientation="h", color="Tipe",
                      color_discrete_map={"Hard Skill":PALETTE[0],"Soft Skill":PALETTE[2]},
                      title=f"Top {top_sk_n} Skill Paling Sering Diminta",
                      labels={"skill":""})
        fig5.update_layout(**lyt())
        fig5.update_yaxes(autorange="reversed")
        st.plotly_chart(fig5, use_container_width=True)
        dl_csv(sk_top, "skill_populer.csv")

with col_sk2:
    with st.container(border=True):
        st.markdown("**Kata Kunci di Deskripsi Pekerjaan**")
        try:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
            n_kata = st.slider("Jumlah kata", 50, 150, 80, key="s3_wc")
            corpus = " ".join(df_jd["text_combined"].dropna())
            wc = WordCloud(width=500, height=400, max_words=n_kata,
                           background_color="white", colormap="Blues",
                           collocations=False).generate(corpus)
            fig_wc, ax = plt.subplots(figsize=(5,4))
            ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
            st.pyplot(fig_wc, use_container_width=True)
            buf = io.BytesIO(); fig_wc.savefig(buf, format="png", bbox_inches="tight")
            st.download_button("⬇ Simpan Word Cloud", buf.getvalue(),
                               "wordcloud.png","image/png", key="dl_wc")
        except ImportError:
            warn("Install `wordcloud` untuk menampilkan visualisasi ini.")

insight("Skill teknis seperti Python, SQL, dan Machine Learning tetap menjadi "
        "yang paling banyak dicari — namun soft skill seperti Communication dan "
        "Management juga tidak kalah penting.")

# ═══ SECTION 4: Level Karir & Work Type ═══════════════════════════
st.markdown("<hr>", unsafe_allow_html=True)
section("👥 Perusahaan Mencari Kandidat Level Apa?")

col_lv1, col_lv2 = st.columns(2, gap="large")

with col_lv1:
    with st.container(border=True):
        EXP_LABEL = {
            "Entry level":"Fresh Graduate / Junior",
            "Mid-Senior level":"Senior",
            "Associate":"Associate",
            "Director":"Direktur",
            "Internship":"Magang",
            "Executive":"Eksekutif",
        }
        exp_cnt = (df_post["formatted_experience_level"].dropna()
                   .map(EXP_LABEL).fillna(df_post["formatted_experience_level"])
                   .value_counts().reset_index())
        exp_cnt.columns = ["Level Karir","Jumlah Lowongan"]
        exp_cnt["pct"] = (exp_cnt["Jumlah Lowongan"]/exp_cnt["Jumlah Lowongan"].sum()*100).round(1)
        fig6 = px.bar(exp_cnt, x="Jumlah Lowongan", y="Level Karir",
                      orientation="h", color="Level Karir",
                      color_discrete_sequence=PALETTE, text="pct",
                      title="Distribusi Level Karir yang Dibutuhkan",
                      labels={"Level Karir":""})
        fig6.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig6.update_layout(**lyt(showlegend=False))
        fig6.update_yaxes(autorange="reversed")
        st.plotly_chart(fig6, use_container_width=True)

with col_lv2:
    with st.container(border=True):
        WT_LABEL = {"Full-time":"Full-time","Part-time":"Part-time",
                    "Contract":"Kontrak","Temporary":"Temporer",
                    "Internship":"Magang","Volunteer":"Sukarela","Other":"Lainnya"}
        wt_cnt = (df_post["formatted_work_type"].dropna()
                  .map(WT_LABEL).fillna(df_post["formatted_work_type"])
                  .value_counts().reset_index())
        wt_cnt.columns = ["Tipe Pekerjaan","Jumlah"]
        fig7 = px.pie(wt_cnt, names="Tipe Pekerjaan", values="Jumlah",
                      hole=0.45, color_discrete_sequence=PALETTE,
                      title="Proporsi Tipe Kontrak Pekerjaan")
        fig7.update_layout(**lyt())
        st.plotly_chart(fig7, use_container_width=True)

insight("Sekitar 30% lowongan terbuka untuk level **Fresh Graduate / Junior** — "
        "artinya peluang masih sangat besar bagi kamu yang baru lulus.")

# ═══ SECTION 5: Benchmark Gaji ════════════════════════════════════
st.markdown("<hr>", unsafe_allow_html=True)
section("💰 Berapa Gaji yang Bisa Kamu Harapkan?")
st.caption("Data gaji dari LinkedIn (dalam USD/tahun, sudah difilter untuk kontrak penuh-waktu).")

if not df_sal.empty:
    with st.container(border=True):
        fig8 = go.Figure()
        colors = PALETTE[:len(df_sal)]
        for i, row in df_sal.iterrows():
            fig8.add_trace(go.Bar(
                name=str(row["level_id"]),
                x=[str(row["level_id"])],
                y=[row["gaji_tengah"]],
                error_y=dict(type="data", symmetric=False,
                             array=[row["gaji_max"]-row["gaji_tengah"]],
                             arrayminus=[row["gaji_tengah"]-row["gaji_min"]]),
                marker_color=PALETTE[i % len(PALETTE)],
                hovertemplate=(
                    f"<b>{row['level_id']}</b><br>"
                    f"Terendah: ${row['gaji_min']:,.0f}<br>"
                    f"Tengah: ${row['gaji_tengah']:,.0f}<br>"
                    f"Tertinggi: ${row['gaji_max']:,.0f}<extra></extra>")))
        fig8.update_layout(**lyt(showlegend=False,
                                  title="Rentang Gaji per Level Karir (USD/Tahun)",
                                  yaxis_title="Gaji per Tahun (USD)",
                                  xaxis_title="Level Karir"))
        st.plotly_chart(fig8, use_container_width=True)
        dl_csv(df_sal[["level_id","gaji_min","gaji_tengah","gaji_max"]], "benchmark_gaji.csv")
    insight("Kenaikan gaji dari level Junior ke Senior bisa mencapai 2–3x lipat. "
            "Investasi dalam skill yang tepat sangat mempengaruhi jalur karir kamu.")
else:
    st.info("Data gaji tidak tersedia.")

# ═══ SECTION 6: Job Catalog AI Evalify ════════════════════════════
st.markdown("<hr>", unsafe_allow_html=True)
section("🤖 Posisi Pekerjaan dalam Sistem AI Evalify")

if df_cat is None:
    warn("File job catalog belum tersedia (perlu <code>git lfs pull</code> dari repo AI). "
         "Bagian ini akan muncul otomatis setelah file tersedia di folder <code>data/</code>.")
else:
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        tn_role = st.slider("Top posisi", 10, 30, 15, key="s6_role")
    with col_c2:
        dom_opts = sorted(explode_pipe(df_cat,"job_domain").unique())
        sel_dom  = st.multiselect("Filter domain", dom_opts,
                                  placeholder="Semua domain", key="s6_dom")
    with col_c3:
        tn_tool = st.slider("Top tools", 10, 25, 15, key="s6_tool")

    df_cf = df_cat.copy()
    if sel_dom:
        df_cf = df_cat[df_cat["job_domain"].apply(
            lambda x: any(d in str(x).split("|") for d in sel_dom) if pd.notna(x) else False)]

    c_col1, c_col2 = st.columns(2, gap="large")
    with c_col1:
        with st.container(border=True):
            rc = df_cf["job_role"].value_counts().head(tn_role).reset_index()
            rc.columns = ["Posisi","Jumlah"]
            fig9 = px.bar(rc, x="Jumlah", y="Posisi", orientation="h",
                          color="Jumlah", color_continuous_scale="Blues",
                          title=f"Top {tn_role} Posisi di Katalog AI Evalify",
                          labels={"Posisi":""})
            fig9.update_layout(**lyt(coloraxis_showscale=False))
            fig9.update_yaxes(autorange="reversed")
            st.plotly_chart(fig9, use_container_width=True)

    with c_col2:
        with st.container(border=True):
            tc2 = explode_pipe(df_cf,"job_required_tools").value_counts().head(tn_tool).reset_index()
            tc2.columns = ["Tools / Teknologi","Jumlah JD"]
            fig10 = px.bar(tc2, x="Jumlah JD", y="Tools / Teknologi",
                           orientation="h", color="Jumlah JD",
                           color_continuous_scale="Teal",
                           title=f"Top {tn_tool} Tools yang Paling Banyak Diminta",
                           labels={"Tools / Teknologi":""})
            fig10.update_layout(**lyt(coloraxis_showscale=False))
            fig10.update_yaxes(autorange="reversed")
            st.plotly_chart(fig10, use_container_width=True)

    with st.container(border=True):
        sen = explode_pipe(df_cf,"job_seniority_level").value_counts().reset_index()
        sen.columns = ["Level Jabatan","Jumlah"]
        show_minor = st.checkbox("Tampilkan level yang sangat kecil (<1%)", key="s6_minor")
        if not show_minor:
            total_s = sen["Jumlah"].sum()
            sen = sen[sen["Jumlah"]/total_s >= 0.01]
        fig11 = px.pie(sen, names="Level Jabatan", values="Jumlah",
                       hole=0.45, color_discrete_sequence=PALETTE,
                       title="Proporsi Level Jabatan di Katalog Evalify")
        fig11.update_layout(**lyt())
        st.plotly_chart(fig11, use_container_width=True)
