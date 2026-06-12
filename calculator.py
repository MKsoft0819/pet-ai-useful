import streamlit as st
import google.genai as genai

# 画面のタイトルや設定
st.set_page_config(page_title="🐾 ペットのAI食事量計算ツール", layout="centered")
st.title("🐾 ペットのAI食事量計算ツール")
st.write("ペットの体重や最近の様子から、AIが最適な1日のごはんの量を計算します。")

# --- 設定エリア ---
st.sidebar.header("🔑 初期設定")
api_key = st.sidebar.text_input("Gemini APIキーを入力してください", type="password")

# --- 入力エリア ---
st.header("1. ペットの情報を入力")
col1, col2 = st.columns(2)

with col1:
    pet_type = st.selectbox("ペットの種類", ["犬", "猫"])
    weight = st.number_input("体重 (kg)", min_value=0.1, max_value=100.0, value=5.0, step=0.1)

with col2:
    food_calorie = st.number_input("ドッグ/キャットフードのカロリー\n(100gあたり/kcal)", min_value=100, max_value=600, value=350)

st.header("2. 最近の様子やライフステージ（AIが分析します）")
consult_text = st.text_area(
    "相談内容・状態の入力例", 
    value="生後6ヶ月で、最近めちゃくちゃ元気いっぱいに走り回っています！"
)

# --- 計算・AI判定エリア ---
if st.button("AIに食事量を計算してもらう", type="primary"):
    if not api_key:
        st.error("左側のメニューからGeminiのAPIキーを入力してください。")
    else:
        with st.spinner("AI獣医が計算中... 🐾"):
            # ① 基本カロリー（RER）の計算
            rer = 70 * (weight ** 0.75)
            
            # ② AI（Gemini）に状態の係数を判定してもらう
            client = genai.Client(api_key=api_key)
            prompt = f"""
            あなたは優秀な獣医です。以下のペットの相談内容から、この子のライフステージや状態を判断し、
            RER（安静時エネルギー）に掛けるべき適切な係数（1.0 〜 3.0の間）を【数字のみ】で1つ返してください。
            余計な説明は一切不要です。
            
            【ペットの種類】: {pet_type}
            【体重】: {weight}kg
            【飼い主からの相談内容】: "{consult_text}"
            
            【係数の目安参考】:
            - 去勢・避妊済みの成犬/成猫: 1.6
            - 未去勢・未避妊の成犬/成猫: 1.8
            - 肥満傾向・高齢: 1.0〜1.2
            - 子犬/子猫（成長期）: 2.0〜3.0
            """
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                coefficient = float(response.text.strip())
            except Exception as e:
                st.warning("AIの自動判定に失敗したため、標準値（1.6）で計算します。")
                coefficient = 1.6

            # ③ 1日の必要カロリー（DER）と食事量の計算
            der = rer * coefficient
            food_grams = (der / food_calorie) * 100

            # ④ 画面に結果を綺麗に表示
            st.success("🎉 計算が完了しました！")
            
            st.metric(label="1日に必要なカロリー (DER)", value=f"{int(der)} kcal")
            st.metric(label="1日あたりのごはんの量", value=f"{int(food_grams)} g")
            
            st.info(f"💡 【AIの分析】この子の状態係数を「{coefficient}」と判定しました。相談内容（{consult_text}）を考慮しています。")