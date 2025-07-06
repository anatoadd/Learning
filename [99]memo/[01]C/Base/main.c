// C言語の基本を網羅したサンプルプログラム

#include <stdio.h>    // 標準入出力ライブラリ
#include <stdlib.h>   // malloc, rand, srand など
#include <time.h>     // 時間取得（乱数の種に使用）

// 挨拶をする関数プロトタイプ
void greet();

int main() {
    // 挨拶関数の呼び出し
    greet();

    // ▼ 条件分岐の例
    int score = 75;
    if (score >= 90) {
        printf("とても優秀です\n");
    } else if (score >= 60) {
        printf("合格です\n");
    } else {
        printf("不合格です\n");
    }

    // ▼ 配列（リスト）の作成と使用
    int scores[5] = {70, 80, 90, 60, 50}; // 5人の点数リスト

    // ▼ リスト内の要素を表示
    printf("\nリスト内の点数:\n");
    for (int i = 0; i < 5; i++) {
        printf("scores[%d] = %d\n", i, scores[i]);
    }

    // ▼ リストの値を変更（2番目の値を100に）
    scores[1] = 100;

    // ▼ リストの要素を追加／削除：Cでは配列の長さは固定なので通常はできませんが、
    //    動的配列（ポインタとmalloc）で実現します（初心者用には下記参考）

    // ▼ ランダムな整数を使う（乱数の例）
    srand(time(NULL));  // 現在の時刻を乱数の種にする
    int rand_val = rand() % 100;  // 0〜99の乱数を生成
    printf("\nランダムな数（0〜99）: %d\n", rand_val);

    // ランダムな数値による条件分岐の例
    if (rand_val < 20) {
        printf("とても低い値\n");
    } else if (rand_val < 70) {
        printf("中間の値\n");
    } else {
        printf("高い値\n");
    }

    return 0;
}

// 挨拶関数の定義
void greet() {
    printf("=== C言語の基本構文デモ ===\n");

    
}
