video 属性
-src   動画ファイルのURL（例: movie.mp4）
-controls   再生・停止などの操作ボタンを表示する
-autoplay   ページ読み込み後、自動で再生（音ありだと多くのブラウザで無効）
-loop   繰り返し再生する
-muted  音をミュート（自動再生したい場合、通常はこれが必須）
-poster 動画のサムネイル画像を指定（再生前に表示）
-width/height   表示サイズの指定

記載順(推奨)
1. 識別 id class	最初
2. 動作・状態	autoplay, controls, loop, muted, disabled, checked	次に
3. ソース・データ	src, href, value, action	中盤
4. サイズ・表示	width, height, style, alt	後半
5. イベント系	onclick, onchange	最後に