import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path


# =========================
# 設定
# =========================

CORRECTIONS_FILE = "corrections.json"


# =========================
# 回転行列
# =========================

ROTATIONS = {
    "X180": [
        1,  0,  0,
        0, -1,  0,
        0,  0, -1
    ],

    "Y180": [
        -1, 0,  0,
         0, 1,  0,
         0, 0, -1
    ],

    "Z180": [
        -1,  0, 0,
         0, -1, 0,
         0,  0, 1
    ]
}


# =========================
# LDraw 1行を補正
# =========================

def apply_correction(line, correction):
    data = line.split()

    # LDraw Type 1 ではない
    if len(data) < 15 or data[0] != "1":
        return line

    # パーツ名
    part_name = data[14]

    # -------------------------
    # 位置
    # -------------------------

    x = float(data[2])
    y = float(data[3])
    z = float(data[4])

    offset = correction.get("offset", [0, 0, 0])

    x += offset[0]
    y += offset[1]
    z += offset[2]

    # -------------------------
    # 元の回転行列
    # -------------------------

    original = [
        float(data[5]), float(data[6]), float(data[7]),
        float(data[8]), float(data[9]), float(data[10]),
        float(data[11]), float(data[12]), float(data[13])
    ]

    # -------------------------
    # 補正回転
    # -------------------------

    rotation_name = correction.get("rotation")

    if rotation_name in ROTATIONS:
        correction_matrix = ROTATIONS[rotation_name]

        # 補正行列 × 元の行列
        result = multiply_matrix(
            correction_matrix,
            original
        )
    else:
        result = original

    # -------------------------
    # 書き戻す
    # -------------------------

    data[2] = f"{x:.6f}"
    data[3] = f"{y:.6f}"
    data[4] = f"{z:.6f}"

    for i in range(9):
        data[5 + i] = f"{result[i]:.6f}"

    return " ".join(data)


# =========================
# 3×3行列の掛け算
# =========================

def multiply_matrix(a, b):
    result = [0] * 9

    for row in range(3):
        for col in range(3):
            result[row * 3 + col] = (
                a[row * 3 + 0] * b[0 * 3 + col]
                + a[row * 3 + 1] * b[1 * 3 + col]
                + a[row * 3 + 2] * b[2 * 3 + col]
            )

    return result


# =========================
# メイン処理
# =========================

def main():

    # corrections.jsonを読み込む
    with open(CORRECTIONS_FILE, "r", encoding="utf-8") as f:
        corrections = json.load(f)

    # ファイル選択画面
    root = tk.Tk()
    root.withdraw()

    input_file = filedialog.askopenfilename(
        title="補正するLDrawファイルを選択",
        filetypes=[
            ("LDraw files", "*.ldr *.mpd"),
            ("All files", "*.*")
        ]
    )

    if not input_file:
        print("ファイルが選択されませんでした。")
        return

    input_path = Path(input_file)

    # 出力ファイル名
    output_path = input_path.with_name(
        input_path.stem + "_corrected" + input_path.suffix
    )

    # LDraw読み込み
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    corrected_lines = []

    correction_count = 0

    for line in lines:

        data = line.split()

        # Type 1でなければそのまま
        if len(data) < 15 or data[0] != "1":
            corrected_lines.append(line)
            continue

        part_name = data[14]

        # 補正データが存在するか
        if part_name in corrections:

            line = apply_correction(
                line,
                corrections[part_name]
            )

            correction_count += 1

        corrected_lines.append(line)

    # 修正済みファイルを書き出す
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(
            line + "\n" if not line.endswith("\n") else line
            for line in corrected_lines
        )

    print("処理完了")
    print(f"入力 : {input_path}")
    print(f"出力 : {output_path}")
    print(f"補正したパーツ数 : {correction_count}")


if __name__ == "__main__":
    main()