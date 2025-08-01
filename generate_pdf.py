from fpdf import FPDF
from PIL import Image
import qrcode
import os
import click

FONT_PATH = "./fonts/ipaexg.ttf"

def generate_pdf(title: str, link: str, photo_paths: list, output_dir: str = None):
    """
    DIY作品のカタログPDFページを生成する関数です。
    
    :param title: 作品のタイトル
    :param link: 作品のリンク
    :param photo_paths: 作品の写真のパスのリスト
    :param output_dir: PDFの出力先ディレクトリ (オプション)
    """
    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()

    # 背景にグラデーション風の効果を作成
    pdf.set_fill_color(245, 247, 250)
    pdf.rect(0, 0, pdf.w, 40, 'F')
    
    # フォント設定
    try:
        pdf.add_font("IPAexGothic", "", FONT_PATH, uni=True)
        pdf.set_font("IPAexGothic", "", 28)
    except Exception as e:
        click.echo(click.style(f"フォントの読み込みに失敗しました: {e}", fg="red"))
        click.echo(click.style("デフォルトフォントを使用します。", fg="yellow"))
        pdf.set_font("Helvetica", "B", 28)

    # タイトル部分のスタイリング
    pdf.set_text_color(51, 51, 51)
    pdf.ln(15)
    
    # タイトルと日付フィールドを左右に配置
    title_y = pdf.get_y()
    pdf.cell(0, 15, text=title, ln=False, align="C")  # ln=Falseで改行しない
    
    # 日付フィールドを右側に配置
    pdf.set_font("IPAexGothic", "", 12)
    pdf.set_text_color(108, 117, 125)
    pdf.set_y(title_y + 2)  # タイトルより少し下に
    pdf.set_x(pdf.w - 60)  # 右端から60mm
    pdf.cell(50, 8, txt="Created: _______________", align="R")
    
    # タイトルフォントとカラーをリセット
    pdf.set_font("IPAexGothic", "", 28)
    pdf.set_text_color(51, 51, 51)
    pdf.set_y(title_y + 15)  # タイトル行の下に移動
    
    # タイトル下にライン
    pdf.set_draw_color(100, 149, 237)
    pdf.set_line_width(0.8)
    pdf.line(40, pdf.get_y() + 5, pdf.w - 40, pdf.get_y() + 5)
    pdf.ln(20)

    # A4サイズでの余白計算（ヘッダー40mm、QRセクション60mm固定、余白10mm）
    # QRコードを最下部に固定配置するため、写真エリアを先に計算
    qr_section_height = 60
    page_height = 297  # A4の高さ
    header_height = 60  # ヘッダー部分
    bottom_margin = 10
    
    # 写真エリアの最大高さを計算
    available_height = page_height - header_height - qr_section_height - bottom_margin
    
    # 写真セクション用の背景
    start_y = pdf.get_y()
    photos_processed = 0
    
    for i, photo_path in enumerate(photo_paths):
        try:
            img = Image.open(photo_path)

            # 写真サイズを大きく調整（2列レイアウト対応）
            if len(photo_paths) == 1:
                max_width = 140.0
                max_height = min(140.0, available_height - 20)
                shadow_offset = 3
            elif len(photo_paths) == 2:
                max_width = 75.0
                max_height = min(95.0, available_height - 20)
                shadow_offset = 2.5
            elif len(photo_paths) <= 4:
                max_width = 55.0
                max_height = min(70.0, (available_height - 30) / 2)
                shadow_offset = 2
            else:
                # 5-6枚も2列レイアウトなので、より大きなサイズに
                max_width = 55.0
                max_height = min(60.0, (available_height - 40) / 3)
                shadow_offset = 2

            width, height = img.size
            aspect_ratio = width / height

            # アスペクト比を保持してリサイズ
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

            # 位置計算（全て2列レイアウトに統一）
            if len(photo_paths) == 1:
                x_pos = (pdf.w - new_width) / 2
                current_y = start_y
            else:
                # 2列グリッド（2-6枚すべて）
                col = i % 2
                row = i // 2
                margin_x = (pdf.w - 2 * new_width) / 3
                margin_y = 8
                x_pos = margin_x + col * (new_width + margin_x)
                current_y = start_y + row * (new_height + margin_y)

            # シャドウ効果
            pdf.set_fill_color(220, 220, 220)
            pdf.rect(x_pos + shadow_offset, current_y + shadow_offset, new_width, new_height, 'F')
            
            # 白い枠
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(x_pos - 0.5, current_y - 0.5, new_width + 1, new_height + 1, 'F')
            
            # 画像を配置
            pdf.image(photo_path, x=x_pos, y=current_y, w=new_width, h=new_height)
            
            photos_processed += 1

        except Exception as e:
            click.echo(click.style(f"写真の読み込みに失敗しました ({photo_path}): {e}", fg="red"))
            if pdf.get_y() < 250:  # エラーメッセージ用の余白がある場合のみ表示
                pdf.set_font("IPAexGothic", "", 8)
                pdf.set_text_color(220, 53, 69)
                pdf.cell(0, 6, txt=f"写真 {i+1} エラー", align="C", ln=True)
                pdf.set_text_color(51, 51, 51)
    
    # QRコードセクションを最下部に固定配置
    qr_section_y = page_height - qr_section_height - bottom_margin
    pdf.set_y(qr_section_y)
    
    # QRコードセクションの背景
    pdf.set_fill_color(248, 249, 250)
    pdf.rect(20, qr_section_y - 3, pdf.w - 40, qr_section_height, 'F')
    
    # QRコード境界線
    pdf.set_draw_color(100, 149, 237)
    pdf.set_line_width(0.5)
    pdf.rect(20, qr_section_y - 3, pdf.w - 40, qr_section_height)
    
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="#2C3E50", back_color="white")
        qr_img_path = "qr_code.png"
        qr_img.save(qr_img_path)

        qr_size = 35  # サイズを45から35に縮小
        qr_x = (pdf.w - qr_size) / 2
        qr_y = pdf.get_y() + 3
        
        # QRコード用の白い背景
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(qr_x - 2, qr_y - 2, qr_size + 4, qr_size + 4, 'F')
        
        pdf.image(qr_img_path, x=qr_x, y=qr_y, w=qr_size, h=qr_size)
        pdf.ln(qr_size + 8)  # 余白を15から8に縮小

        # リンクテキストのスタイリング（コンパクト化）
        pdf.set_font("IPAexGothic", "", 12)  # サイズを14から12に縮小
        pdf.set_text_color(100, 149, 237)
        pdf.cell(0, 6, txt="詳細はこちらから", align="C", ln=True)  # 高さを8から6に縮小
        pdf.set_text_color(51, 51, 51)

        os.remove(qr_img_path)
    except Exception as e:
        click.echo(click.style(f"QRコードの生成に失敗しました: {e}", fg="red"))
        pdf.set_font("IPAexGothic", "", 12)
        pdf.set_text_color(220, 53, 69)
        pdf.cell(0, 10, txt="QRコードの生成に失敗しました。", align="C", ln=True)
        pdf.set_text_color(51, 51, 51)

    base_filename = f"{title.replace(' ', '_')}_catalog.pdf"
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, base_filename)
    else:
        output_filename = base_filename

    pdf.output(output_filename)
    return output_filename
