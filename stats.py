import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.table import Table

def load_results(filepath="pacman_result.json"):
    if not os.path.exists(filepath):
        print("❌ Fichier JSON non trouvé.")
        return []
    with open(filepath, "r") as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            print("❌ Erreur de lecture du JSON.")
            return []

def generate_dataframe(results):
    df = pd.DataFrame(results)
    df['timeout'] = df['time out'].astype(str) == 'true'
    df['partie'] = df.index + 1
    return df

def plot_pie_chart(df):
    result_counts = df['result'].value_counts()
    plt.figure(figsize=(5, 5))
    plt.pie(result_counts, labels=result_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title("Répartition des résultats (win/lose)")
    plt.tight_layout()
    plt.show()



def show_summary_table(df):
    total = len(df)
    wins = (df['result'] == 'win').sum()
    losses = (df['result'] == 'lose').sum()
    timeouts = df['timeout'].sum()
    avg_score = df['score'].mean()
    avg_time = df['time'].mean()
    avg_lives = df['lives'].mean()

    summary_data = [
        ["Total parties", total],
        ["Victoires", wins],
        ["Défaites", losses],
        ["Timeouts", timeouts],
        ["Score moyen", f"{avg_score:.1f}"],
        ["Durée moyenne (s)", f"{avg_time:.1f}"],
        ["Vies restantes moyennes", f"{avg_lives:.2f}"]
    ]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.set_axis_off()
    table = Table(ax, bbox=[0, 0, 1, 1])
    cell_width = 1.0 / 2
    cell_height = 1.0 / len(summary_data)

    # Header
    table.add_cell(0, 0, cell_width, cell_height, text="Statistique", loc='center', facecolor='lightgray')
    table.add_cell(0, 1, cell_width, cell_height, text="Valeur", loc='center', facecolor='lightgray')

    for i, (label, value) in enumerate(summary_data):
        table.add_cell(i+1, 0, cell_width, cell_height, text=label, loc='center')
        table.add_cell(i+1, 1, cell_width, cell_height, text=str(value), loc='center')

    for i in range(len(summary_data)+1):
        for j in range(2):
            table[i, j].visible_edges = 'open' if i == 0 else 'closed'

    ax.add_table(table)
    plt.title("Résumé des statistiques")
    plt.tight_layout()
    plt.show()

def main():
    results = load_results("pacman_result.json")
    if not results:
        return
    df = generate_dataframe(results)
    show_summary_table(df)
    plot_pie_chart(df)


if __name__ == "__main__":
    main()
