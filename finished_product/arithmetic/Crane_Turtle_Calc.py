#Crane_Turtle_Calc.py
def calculate_crane_and_turtle(heads, legs):
    # 鶴が x 羽、亀が y 匹とすると
    # x + y = heads
    # 2x + 4y = legs
    # これを連立方程式で解く
    for cranes in range(heads + 1):
        turtles = heads - cranes
        if 2 * cranes + 4 * turtles == legs:
            return cranes, turtles
    return None, None

def calculate_heads_and_legs(cranes, turtles):
    heads = cranes + turtles
    legs = 2 * cranes + 4 * turtles
    return heads, legs

def main():
    print("鶴亀算プログラム")
    print("1: 頭と足の総数から鶴と亀の数を計算")
    print("2: 鶴と亀の数から頭と足の総数を計算")
    choice = input("選択してください (1 または 2): ")

    if choice == "1":
        heads = int(input("頭の総数を入力してください: "))
        legs = int(input("足の総数を入力してください: "))
        cranes, turtles = calculate_crane_and_turtle(heads, legs)

        if cranes is not None and turtles is not None:
            print(f"鶴: {cranes} 羽, 亀: {turtles} 匹")
        else:
            print("条件を満たす鶴と亀の数は存在しません。")

    elif choice == "2":
        cranes = int(input("鶴の数を入力してください: "))
        turtles = int(input("亀の数を入力してください: "))
        heads, legs = calculate_heads_and_legs(cranes, turtles)
        print(f"頭の総数: {heads}, 足の総数: {legs}")

    else:
        print("無効な選択です。1 または 2 を入力してください。")

if __name__ == "__main__":
    main()