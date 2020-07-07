def plot_statistic_values(results_osv, results_linux, title):
    min_osv, min_linux = min(results_osv), min(results_linux)
    max_osv, max_linux = max(results_osv), max(results_linux)
    mean_osv, mean_linux = st.mean(results_osv), st.mean(results_linux)
    stand_osv, stand_linux = st.stdev(results_osv), st.stdev(results_linux)

    labels = ['min', 'max', 'mean', 'standard deviation']
    data_osv = [min_osv, max_osv, mean_osv, stand_osv]
    data_linux = [min_linux, max_linux, mean_linux, stand_linux]
    xpos = range(4)
    plt.xticks(xpos, labels)
    plt.ylabel('time(ms)')
    plt.title(title)
    plt.bar(xpos-0.2, data_osv, width=0.5, label='OSv Instance')
    plt.bar(xpos+0.2, data_linux, width=0.5, label='Linux Instance')
    plt.legend()
    plt.show()
    return