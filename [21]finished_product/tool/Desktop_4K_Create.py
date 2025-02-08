from PIL import Image, ImageDraw

def generate_gradient_image(width, height, start_color, end_color, output_file):
    """
    4Kグラデーション画像を生成する関数

    :param width: 画像の幅 (ピクセル)
    :param height: 画像の高さ (ピクセル)
    :param start_color: 開始色 (R, G, B のタプル)
    :param end_color: 終了色 (R, G, B のタプル)
    :param output_file: 保存先のファイルパス
    """
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)

    for y in range(height):
        r = start_color[0] + (end_color[0] - start_color[0]) * y // height
        g = start_color[1] + (end_color[1] - start_color[1]) * y // height
        b = start_color[2] + (end_color[2] - start_color[2]) * y // height
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    image.save(output_file)
    print(f"画像が保存されました: {output_file}")

# 例: 4K解像度で青から白へのグラデーション画像を生成
generate_gradient_image(
    width=3840,
    height=2160,
    start_color=(0, 0, 255),  # 青
    end_color=(255, 255, 255),  # 白
    output_file="gradient_background.png"
)
