import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path


# ============================================================
# 設定
# ============================================================

# correct.py と同じフォルダにある corrections.json を使用
BASE_DIR = Path(__file__).resolve().parent
CORRECTIONS_FILE = BASE_DIR / "corrections.json"


# ============================================================
# 回転行列
# ============================================================

ROTATIONS = {
    # X軸
    "X90": [
         1,  0,  0,
         0,  0, -1,
         0,  1,  0
    ],

    "X180": [
         1,  0,  0,
         0, -1,  0,
         0,  0, -1
    ],

    "X270": [
         1,  0,  0,
         0,  0,  1,
         0, -1,  0
    ],

    # Y軸
    "Y90": [
         0,  0,  1,
         0,  1,  0,
        -1,  0,  0
    ],

    "Y180": [
        -1,  0,  0,
         0,  1,  0,
         0,  0, -1
    ],

    "Y270": [
         0,  0, -1,
         0,  1,  0,
         1,  0,  0
    ],

    # Z軸
    "Z90": [
         0, -1,  0,
         1,  0,  0,
         0,  0,  1
    ],

    "Z180": [
        -1,  0,  0,
         0, -1,  0,
         0,  0,  1
    ],

    "Z270": [
         0,  1,  0,
        -1,  0,  0,
         0,  0,  1
    ]
}

# ============================================================
# 3×3行列の掛け算
# ============================================================

def multiply_matrix(a, b):
    result = [0.0] * 9

    for row in range(3):
        for col in range(3):
            result[row * 3 + col] = (
                a[row * 3 + 0] * b[0 * 3 + col]
                + a[row * 3 + 1] * b[1 * 3 + col]
                + a[row * 3 + 2] * b[2 * 3 + col]
            )

    return result


# ============================================================
# 行列 × ベクトル
# ============================================================

def multiply_vector(matrix, vector):
    x, y, z = vector

    return [
        matrix[0] * x + matrix[1] * y + matrix[2] * z,
        matrix[3] * x + matrix[4] * y + matrix[5] * z,
        matrix[6] * x + matrix[7] * y + matrix[8] * z
    ]


# ============================================================
# 1行のLDrawデータを補正
# ============================================================

def apply_correction(line, correction):

    data = line.split()

    # Type 1 のパーツ行ではない
    if len(data) < 15 or data[0] != "1":
        return line

    # --------------------------------------------------------
    # 位置
    # --------------------------------------------------------

    x = float(data[2])
    y = float(data[3])
    z = float(data[4])

    position = [x, y, z]

    # --------------------------------------------------------
    # 元の回転行列
    # --------------------------------------------------------

    original_matrix = [
        float(data[5]),
        float(data[6]),
        float(data[7]),

        float(data[8]),
        float(data[9]),
        float(data[10]),

        float(data[11]),
        float(data[12]),
        float(data[13])
    ]

    # --------------------------------------------------------
    # ① 回転を適用
    # --------------------------------------------------------

    rotation_names = correction.get("rotation")

    final_matrix = original_matrix

    if rotation_names:

        # 1個だけ指定された場合にも対応
        if isinstance(rotation_names, str):
            rotation_names = [rotation_names]

        # 指定された順番に回転を適用
        for rotation_name in rotation_names:

            if rotation_name not in ROTATIONS:
                print(
                    f"WARNING: 未知の回転指定: {rotation_name}"
                )
                continue

            correction_matrix = ROTATIONS[rotation_name]

            final_matrix = multiply_matrix(
                correction_matrix,
                final_matrix
            )

    else:
        final_matrix = original_matrix

    # --------------------------------------------------------
    # ② 回転後の座標系で offset を適用
    # --------------------------------------------------------

    offset = correction.get("offset") or [0, 0, 0]

    # offsetを回転後の座標系から
    # ワールド座標系へ変換
    rotated_offset = multiply_vector(
        final_matrix,
        offset
    )

    position[0] += rotated_offset[0]
    position[1] += rotated_offset[1]
    position[2] += rotated_offset[2]

    # --------------------------------------------------------
    # データを書き戻す
    # --------------------------------------------------------

    data[2] = f"{position[0]:.6f}"
    data[3] = f"{position[1]:.6f}"
    data[4] = f"{position[2]:.6f}"

    for i in range(9):
        data[5 + i] = f"{final_matrix[i]:.6f}"

    return " ".join(data)


# ============================================================
# メイン
# ============================================================

def main():

    # ========================================================
    # JSONファイル
    # ========================================================

    BASE_DIR = Path(__file__).resolve().parent

    CORRECTIONS_FILE = BASE_DIR / "corrections.json"

    # ========================================================
    # corrections.json 読み込み
    # ========================================================

    if not CORRECTIONS_FILE.exists():
        print("ERROR:")
        print(f"corrections.json が見つかりません:")
        print(CORRECTIONS_FILE)
        return

    with open(CORRECTIONS_FILE, "r", encoding="utf-8") as f:
        corrections = json.load(f)

    # ========================================================
    # LDrawファイルを選択
    # ========================================================

    root = tk.Tk()
    root.withdraw()

    input_file = filedialog.askopenfilename(
        title="処理するLDrawファイルを選択",
        filetypes=[
            ("LDraw files", "*.ldr *.mpd"),
            ("All files", "*.*")
        ]
    )

    if not input_file:
        print("ファイルが選択されませんでした。")
        return

    input_path = Path(input_file)

    # ========================================================
    # 出力ファイル名
    # ========================================================

    output_path = input_path.with_name(
        input_path.stem + "_corrected" + input_path.suffix
    )

    # ========================================================
    # LDrawファイル読み込み
    # ========================================================

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    corrected_lines = []

    rename_count = 0
    correction_count = 0

    # ========================================================
    # 各行を処理
    # ========================================================

    for line in lines:

        data = line.split()

        # Type 1ではない
        if len(data) < 15 or data[0] != "1":
            corrected_lines.append(line)
            continue

        # ----------------------------------------------------
        # パーツ名
        # ----------------------------------------------------

        original_part_name = data[14]

        # ----------------------------------------------------
        # .datパーツだけを処理
        # ----------------------------------------------------

        if original_part_name.endswith(".dat"):

            part_path = Path(original_part_name)
            part_name = part_path.stem
            extension = part_path.suffix

            # ------------------------------------------------
            # パーツ名から数字以外をすべて削除
            # ------------------------------------------------

            new_part_name = "".join(
                char for char in part_name
                if char.isdigit()
            )

            if new_part_name != part_name:

                data[14] = new_part_name + extension

                rename_count += 1

                print(
                    f"Rename: {original_part_name} -> {data[14]}"
                )

            # ------------------------------------------------
            # 名称変換後のパーツ名で補正を検索
            # ------------------------------------------------

            new_part_name = Path(data[14]).name

            if new_part_name in corrections:

                new_line = apply_correction(
                    " ".join(data),
                    corrections[new_part_name]
                )

                corrected_lines.append(new_line + "\n")
                correction_count += 1

            else:

                corrected_lines.append(
                    " ".join(data) + "\n"
                )

        else:

            # ------------------------------------------------
            # submodelなど、.datではないものは完全にそのまま
            # ------------------------------------------------

            corrected_lines.append(line)
    # ========================================================
    # 出力
    # ========================================================

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(corrected_lines)

    # ========================================================
    # 結果
    # ========================================================

    print()
    print("========================================")
    print("LDraw処理完了")
    print("========================================")
    print(f"入力ファイル       : {input_path}")
    print(f"出力ファイル       : {output_path}")
    print(f"名称変換したパーツ : {rename_count}")
    print(f"補正したパーツ     : {correction_count}")
    print("========================================")


# ============================================================
# 実行
# ============================================================

if __name__ == "__main__":
    main()