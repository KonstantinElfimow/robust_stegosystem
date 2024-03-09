import matplotlib.pyplot as plt


def build_graphic(title: str,
                  x: list,
                  x_label: str,
                  distance_average_hash: list,
                  distance_phash: list,
                  distance_dhash: list,
                  y_max: int):
    plt.plot(x, distance_average_hash, label='Average Hash', marker='o')
    plt.plot(x, distance_phash, label='pHash', marker='o')
    plt.plot(x, distance_dhash, label='dHash', marker='o')
    # добавление легенды и заголовка
    plt.legend()
    plt.title(title)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel('Расстояние Хемминга', fontsize=12)

    # включаем дополнительные отметки на осях
    plt.minorticks_on()

    plt.xlim([0., max(x) + 1])
    plt.ylim([0., y_max])
    # включаем основную сетку
    plt.grid(which='major')
    # включаем дополнительную сетку
    plt.grid(which='minor', linestyle=':')
    plt.tight_layout()
    plt.savefig(f'results/{title}.png')
