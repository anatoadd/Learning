// C言語基礎学習用

#include <stdio.h>    // 入出力
#include <stdlib.h>   // malloc, rand
#include <time.h>     // time関数（乱数の種）

// ================================
// 関数プロトタイプ宣言
// ================================
void greet();                       // 引数なし・戻り値なしの関数
int square(int x);                 // 引数あり・戻り値ありの関数
void printArray(int* arr, int size); // ポインタを使った配列表示

int main() {
    // 挨拶
    greet();

    // ================================
    // whileループの例
    // ================================
    int i = 0;
    printf("\nwhile ループで 0～4 を表示:\n");
    while (i < 5) {
        printf("i = %d\n", i);
        i++;
    }

    // ================================
    // do-whileループの例
    // ================================
    int input;
    printf("\ndo-while ループで 10が入力されるまで繰り返す:\n");
    do {
        printf("10を入力してください: ");
        scanf("%d", &input);
    } while (input != 10);
    printf("10が入力されました！\n");

    // ================================
    // for文の応用（配列の合計）
    // ================================
    int scores[] = {80, 70, 60, 90, 100};
    int total = 0;
    int count = sizeof(scores) / sizeof(scores[0]);

    for (int j = 0; j < count; j++) {
        total += scores[j];
    }
    printf("\nfor文で配列の合計を計算: %d\n", total);

    // ================================
    // 関数の引数と戻り値の使用例
    // ================================
    int num = 6;
    int result = square(num); // 関数呼び出し
    printf("\n%dの2乗は%dです\n", num, result);

    // ================================
    // ポインタを使ったリスト操作（初級+）
    // ================================
    int* dynamicArray;
    int length = 5;

    // 動的にメモリを確保
    dynamicArray = (int*)malloc(length * sizeof(int));

    // 乱数初期化
    srand(time(NULL));

    // 動的配列にランダムな数値を格納
    for (int k = 0; k < length; k++) {
        dynamicArray[k] = rand() % 100;
    }

    printf("\n動的配列（乱数入り）をポインタで出力:\n");
    printArray(dynamicArray, length);

    // メモリを開放
    free(dynamicArray);

    return 0;
}

// ================================
// 引数なし・戻り値なしの関数
// ================================
void greet() {
    printf("=== C言語 総合構文デモ ===\n");
}

// ================================
// 引数あり・戻り値ありの関数
// ================================
int square(int x) {
    return x * x;
}

// ================================
// ポインタで配列を受け取って出力する関数
// ================================
void printArray(int* arr, int size) {
    for (int i = 0; i < size; i++) {
        printf("arr[%d] = %d\n", i, arr[i]);
    }
}
