// C言語の基本を網羅したサンプルプログラム

#include <stdio.h>

// 関数プロトタイプ宣言
void greet(); // 挨拶をする関数

// メイン関数
int main() {
    // 変数の宣言と初期化
    int num1 = 10; // 数値1
    int num2 = 5;  // 数値2
    int sum;       // 合計を格納する変数

    // 挨拶関数の呼び出し
    greet();

    // 加算
    sum = num1 + num2;

    // 結果の表示
    printf("数値1: %d\n", num1);
    printf("数値2: %d\n", num2);
    printf("合計: %d\n", sum);

    return 0;
}

// 挨拶をする関数の定義
void greet() {
    printf("こんにちは、C言語の世界へようこそ！\n");
}
