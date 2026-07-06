import os


def read_deck_csv() -> list[int]:
    """deck.csv を読み込んでカードIDのリストを返す。

    Returns:
        list[int]: デッキに含まれるカードIDのリスト（60枚）。
    """
    file_path = "deck.csv"
    if not os.path.exists(file_path):
        file_path = "/kaggle_simulations/agent/" + file_path
    with open(file_path, "r") as file:
        csv = file.read().split("\n")
    return [int(csv[i]) for i in range(60)]
