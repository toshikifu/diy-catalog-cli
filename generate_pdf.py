from fpdf import FPDF
from PIL import Image
import qrcode
import os
import click

FONT_PATH = "./fonts/ipaexg.ttf"

def generate_pdf(title: str, link: str, photo_path: str, output_dir: str = None):
    """
    DIY作品のカタログPDFページを生成する関数です。
    
    :param title: 作品のタイトル
    :param link: 作品のリンク
    :param photo_path: 作品の写真のパス
    :param output_dir: PDFの出力先ディレクトリ (オプション)
    """
    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()

    try:
        pdf.add_font("IPAexGothic", "", FONT_PATH, uni=True)
        pdf.set_font("IPAexGothic", "", 24)
    except Exception as e:
        click.echo(click.style(f"フォントの読み込みに失敗しました: {e}", fg="red"))
        click.echo(click.style("デフォルトフォントを使用します。", fg="yellow"))
        pdf.set_font("Helvetica", "", 24)

    pdf.set_text_color(24, 44, 61)

    pdf.cell(0, 20, text=title, ln=True, align="C")
    pdf.ln(10)

    try:
        img = Image.open(photo_path)

        max_width = 180.0
        max_height = 180.0

        width, height = img.size
        aspect_ratio = width / height

        if width > height:
            new_width = max_width
            new_height = max_width / aspect_ratio
            if new_height > max_height:
                new_height = max_height
                new_width = max_height * aspect_ratio
        else:
            new_height = max_height
            new_width = max_height * aspect_ratio
            if new_width > max_width:
                new_width = max_width
                new_height = max_width / aspect_ratio

        pdf.image(photo_path, x=(pdf.w - new_width) / 2, y=pdf.get_y(), w=new_width, h=new_height)
        pdf.ln(new_height + 10)
    except Exception as e:
        click.echo(click.style(f"写真の読み込みに失敗しました: {e}", fg="red"))
        pdf.set_font("IPAexGothic", "", 24)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, txt="写真の表示に失敗しました。", align="C", ln=True)
        pdf.set_text_color(0, 0, 0)

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img_path = "qr_code.png"
        qr_img.save(qr_img_path)

        qr_size = 50

        pdf.image(qr_img_path, x=(pdf.w - qr_size) / 2, y=pdf.get_y(), w=qr_size, h=qr_size)
        pdf.ln(qr_size + 5)

        pdf.set_font("IPAexGothic", "", 24)
        pdf.set_text_color(0, 0, 255)
        pdf.cell(0, 10, txt="作品のリンク:", align="C", ln=True)
        pdf.set_text_color(0, 0, 0)

        os.remove(qr_img_path)
    except Exception as e:
        click.echo(click.style(f"QRコードの生成に失敗しました: {e}", fg="red"))
        pdf.set_font("IPAexGothic", "", 24)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, txt="QRコードの生成に失敗しました。", align="C", ln=True)
        pdf.set_text_color(0, 0, 0)

    base_filename = f"{title.replace(' ', '_')}_catalog.pdf"
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, base_filename)
    else:
        output_filename = base_filename

    pdf.output(output_filename)
    return output_filename
