import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

st.markdown(
    """
    <div style='text-align: center; margin-top: 30px;'>
        <a href='https://www.linkedin.com/in/lingyu-maxwell-lai' target='_blank' style='text-decoration: none;'>
            <button style='background-color: #0077B5; color: white; border: none; border-radius: 5px; padding: 10px 20px; font-size: 16px; cursor: pointer;'>
                🔗 LinkedIn:Maxwell Lai
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# 页面设置
st.set_page_config(page_title="RestoSuite 桌台码生成器", layout="centered")
st.title("📦 RestoSuite QR 桌台码生成器")
st.caption("上传 QR 图像，系统生成标准标签样式并导出 PDF")

# 加载字体
@st.cache_data
def load_font(size=48):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", size)
    except:
        return ImageFont.load_default()

font_large = load_font(72)

# 自动裁剪透明留白的 logo
def trim_logo(img):
    bbox = img.getbbox()
    return img.crop(bbox)

# 尝试加载 logo
try:
    logo_raw = Image.open("logo.png").convert("RGBA")
    logo_img = trim_logo(logo_raw).resize((480, 120))
except:
    logo_img = None
    st.warning("⚠️ 未找到 logo.png，标签中将省略 Logo。")

# 上传 QR 图像
qr_files = st.file_uploader("📷 上传 QR 图像（如 A1.png、B2.jpg）", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# 样式定义
label_w, label_h = 800, 1000
qr_size = (460, 460)
qr_offset = (170, 140)
text_pos_y = 650
logo_pos_y = 740
labels_per_page = 9
cols, rows = 3, 3

# 生成单个标签
def create_label(qr_img, desk_name):
    canvas = Image.new("RGB", (label_w, label_h), "white")
    draw = ImageDraw.Draw(canvas)

    # 蓝色圆角边框
    draw.rounded_rectangle((10, 10, label_w - 10, label_h - 10), radius=40, outline="#237EFB", width=13)

    # QR
    qr_resized = qr_img.resize(qr_size)
    canvas.paste(qr_resized, qr_offset, qr_resized)

    # 桌号文字（加粗）
    bbox = draw.textbbox((0, 0), desk_name, font=font_large)
    w = bbox[2] - bbox[0]
    draw.text(((label_w - w) // 2, text_pos_y), desk_name, font=font_large, fill="black")

    # Logo
    if logo_img:
        canvas.paste(logo_img, ((label_w - logo_img.width) // 2, logo_pos_y), logo_img)

    return canvas

if qr_files:
    st.success(f"✅ 已上传 {len(qr_files)} 张二维码，将生成标签并分页导出")

    page_w = label_w * cols
    page_h = label_h * rows
    pages = []

    for i in range(0, len(qr_files), labels_per_page):
        canvas = Image.new("RGB", (page_w, page_h), "white")

        for idx, file in enumerate(qr_files[i:i + labels_per_page]):
            qr = Image.open(file).convert("RGBA")
            desk_name = os.path.splitext(file.name)[0]
            label = create_label(qr, desk_name)

            row, col = divmod(idx, cols)
            x = col * label_w
            y = row * label_h
            canvas.paste(label, (x, y))

        pages.append(canvas)

    # 预览
    st.subheader("🖼️ 标签预览（第1页）：")
    st.image(pages[0])

    # 导出 PDF
    pdf_bytes = BytesIO()
    pages[0].save(pdf_bytes, format="PDF", save_all=True, append_images=pages[1:])
    st.download_button("📥 下载标签 PDF", data=pdf_bytes.getvalue(), file_name="RestoSuite_Tags.pdf", mime="application/pdf")
