import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os


def read_values(path):
    values = []
    with open(path, 'r') as f:
        for line in f:
            values.append(line)
        f.close()
    return values


def save_bar_chart(values_linux, values_osv, title, ylabel, filename):
    labels = ['min', 'max', 'mean', 'stand']
    values_linux = [np.min(values_linux), np.max(values_linux), np.mean(values_linux), np.std(values_linux)]
    values_osv = [np.min(values_osv), np.max(values_osv), np.mean(values_osv), np.std(values_osv)]
    x = np.arange(len(labels))
    width = 0.35
    plt.bar(x-width/2, values_linux, color=['black'], width=width,  label='Linux')
    plt.bar(x+width/2, values_osv, color=['grey'], width=width, label='OSV')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x, labels)
    plt.legend(loc= 'upper right')
    plt.savefig(filename)


os.chdir('../results')

linux_boot_times = read_values('linux-boot-times.txt')
osv_boot_times = read_values('osv-boot-times.txt')
save_bar_chart(linux_boot_times, osv_boot_times, 'Boot Times', 'Time in ms', 'boot-times.png')

linux_execution_times = read_values('linux-execution-times.txt')
osv_execution_times = read_values('osv-execution-times.txt')
save_bar_chart(linux_execution_times, osv_execution_times, 'Execution Times', 'Time in ms', 'execution-times.png')

'''
linux = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
osv = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
x_hello = range(10)

plt.plot(x_hello, linux, label='linux')
plt.plot(x_hello, osv, label='osv')
plt.xlabel('time')
plt.ylabel('percent')
plt.title('utilisation')
plt.legend(loc='upper right')
plt.show()
'''


