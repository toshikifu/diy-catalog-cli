import os
import click
from generate_pdf import generate_pdf

@click.command()
def create_catalog_page():
    """
    DIY作品のカタログPDFページを作成します．
    """
    click.echo("--- DIY作品のカタログPDFページを作成 ---")
    click.echo("以下の質問に答えて，作品情報を入力してください")

    title = click.prompt("作品のタイトル")

    link = click.prompt("作品のリンク(例: https://youtu.be/xxxx)", type=str)
    if not link.startswith(("https://", "http://")):
        click.echo("形式が無効です", err=True)
        click.echo("リンクはhttp://またはhttps://で始まる必要があります", err=True)
        return
    
    photo_paths = []
    click.echo("写真を追加してください（最大6枚まで、空白でEnterを押すと終了）")
    
    while len(photo_paths) < 6:
        prompt_text = f"写真のパス ({len(photo_paths)+1}/6)：" if len(photo_paths) == 0 else f"写真のパス ({len(photo_paths)+1}/6、空白で終了）："
        photo_path = click.prompt(prompt_text, type=str, default="", show_default=False)
        
        if photo_path.strip() == "":
            if len(photo_paths) == 0:
                click.echo("少なくとも1枚の写真が必要です", err=True)
                continue
            else:
                break
        
        expanded_path = os.path.expanduser(photo_path)
        if not expanded_path.endswith(('.jpg', '.jpeg', '.png')):
            click.echo("写真のパスはjpg, jpeg, png形式である必要があります", err=True)
            continue

        if os.path.exists(expanded_path):
            photo_paths.append(expanded_path)
            click.echo(f"写真ファイル： {expanded_path} が追加されました")
        else:
            click.echo(f"写真ファイル： {expanded_path} が見つかりません", err=True)

    default_downloads_path = os.path.expanduser('~/Downloads')
    output_dir = click.prompt("出力先ディレクトリ (Output directory)", type=click.Path(), default=default_downloads_path)
    # Add a note about Windows compatibility if necessary, or implement more robust path detection.
    # For now, we'll rely on os.path.expanduser and click.Path validation.

    click.echo("以下の情報でカタログページを作成します：")
    click.echo(f"タイトル: {title}")
    click.echo(f"リンク: {link}")
    click.echo(f"写真パス: {', '.join(photo_paths)}")
    click.echo(f"出力先ディレクトリ: {output_dir}")


    # ここでPDFページを作成する処理を追加します
    try:
        click.echo("PDFページの作成処理を実行中...")
        output_file = generate_pdf(title, link, photo_paths, output_dir)
        click.echo(click.style(f"PDFページが作成されました: {output_file}", fg='green'))
    except Exception as e:
        click.echo(click.style(f"PDFページの作成中にエラーが発生しました: {e}", fg='red'))

if __name__ == "__main__":
    create_catalog_page()
