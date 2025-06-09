import os
import click

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
    
    while True:
        photo_path = click.prompt("作品の写真のパス：", type=str)
        if not photo_path.endswith(('.jpg', '.jpeg', '.png')):
            click.echo("写真のパスはjpg, jpeg, png形式である必要があります", err=True)

        if os.path.exists(photo_path):
            click.echo(f"写真ファイル： {photo_path} が見つかりました")
            break
        else:
            click.echo(f"写真ファイル： {photo_path} が見つかりません", err=True)

    click.echo("以下の情報でカタログページを作成します：")
    click.echo(f"タイトル: {title}")
    click.echo(f"リンク: {link}")
    click.echo(f"写真パス: {photo_path}")

    # ここでPDFページを作成する処理を追加します
    click.echo("PDFページの作成処理を実行中...")
    click.echo("カタログページの作成が完了しました！")

if __name__ == "__main__":
    create_catalog_page()
