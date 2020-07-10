import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os


def read_values(path):
    values = []
    f = open(path, 'r')
    values = f.read().split('\n')
    f.close()
    return np.array(values[:-1]).astype(np.float128)


def save_bar_chart(values_linux, values_osv, title, ylabel, filename):
    labels = ['min', 'max', 'mean', 'stand']
    values_linux_reduced = [np.min(values_linux), np.max(values_linux), np.mean(values_linux), np.std(values_linux)]
    values_osv_reduced = [np.min(values_osv), np.max(values_osv), np.mean(values_osv), np.std(values_osv)]
    print(values_linux_reduced)
    print(values_osv_reduced)
    x = np.arange(len(labels))
    width = 0.35
    plt.bar(x-width/2, values_linux_reduced, color=['black'], width=width,  label='Linux')
    plt.bar(x+width/2, values_osv_reduced, color=['grey'], width=width, label='OSV')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x, labels)
    plt.legend(loc= 'upper right')
    plt.savefig(filename)


os.chdir('../results')

linux_boot_times = read_values('linux-boot-times.txt')
osv_boot_times = read_values('osv-boot-times.txt')
print(linux_boot_times)
print(osv_boot_times)
save_bar_chart(linux_boot_times, osv_boot_times, 'Boot Times', 'Time in ms', 'boot-times.png')

linux_stop_times = read_values('linux-stop-times.txt')
osv_stop_times = read_values('osv-stop-times.txt')
print(linux_stop_times)
print(osv_stop_times)
save_bar_chart(linux_stop_times, osv_stop_times, 'Shutdown Times', 'Time in ms', 'stop-times.png')

linux_network_execution_times = read_values('linux-network-execution-times.txt')
osv_network_execution_times = read_values('osv-network-execution-times.txt')
print(linux_network_execution_times)
print(osv_network_execution_times)
save_bar_chart(linux_network_execution_times, osv_network_execution_times, 'Execution Times (Network-I/O Task)', 'Time in ms', 'network-execution-times.png')


linux_disk_execution_times = read_values('linux-disk-execution-times.txt')
osv_disk_execution_times = read_values('osv-disk-execution-times.txt')
print(linux_disk_execution_times)
print(osv_disk_execution_times)
save_bar_chart(linux_disk_execution_times, osv_disk_execution_times, 'Execution Times (Disk-I/O Task)', 'Time in ms', 'disk-execution-times.png')


