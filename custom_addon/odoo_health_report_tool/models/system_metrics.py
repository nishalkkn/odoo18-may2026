# -*- coding: utf-8 -*-
from odoo import models, api, tools
import psutil
import os
import subprocess

from odoo.modules import get_module_path
from odoo.tools.safe_eval import time


class SystemMetrics(models.Model):
    _name = 'system.metrics'
    _description = 'System Metrics'

    # @api.model
    # def get_metrics_data(self):
    #     """ Get CPU, Memory, Server, Process memory and disk performance Usage"""        # cpu_usage = psutil.cpu_percent(interval=1)
    #     pid = os.getpid()
    #     process = psutil.Process(pid)
    #
    #     # cpu utilization
    #     cpu_count = psutil.cpu_count()
    #     cpu_times = psutil.cpu_times_percent(interval=1)
    #     cpu_user_times = cpu_times.user
    #     cpu_system_times = cpu_times.system
    #     cpu_idle_times = cpu_times.idle
    #     cpu_iowait_times = cpu_times.iowait
    #     cpu_irq_times = cpu_times.irq
    #     load_avg = psutil.getloadavg()
    #
    #     # Get Memory Usage
    #     memory_info = process.memory_info()
    #     memory_info_rss = (memory_info.rss / (1024 ** 2))
    #     memory_info_vms = (memory_info.vms / (1024 ** 2))
    #     memory_info_shared = (memory_info.shared / (1024 ** 2))
    #     memory_info_text = (memory_info.text / (1024 ** 2))
    #     memory_info_data = (memory_info.data / (1024 ** 2))
    #
    #     # server memory
    #     memory = psutil.virtual_memory()
    #     total_memory = memory.total / (1024.0 ** 2)
    #     cached_memory = (memory.cached / (1024 ** 2))
    #     buffered_memory = (memory.buffers / (1024 ** 2))
    #     shared_memory = (memory.shared / (1024 ** 2))
    #
    #     storage = psutil.virtual_memory()
    #     used_ram_percent = storage.percent  #memory usage
    #     total_ram = round(storage.total / (1024.0 ** 2), 2)  #total memory
    #     used_mem = (total_ram * used_ram_percent)/100
    #     free_mem = total_ram - used_mem
    #
    #     allowed_workers = (cpu_count * 2) + 1
    #     current_workers = tools.config['workers']
    #     min_cpu_count = (current_workers - 1)/2
    #
    #     #Disk performance
    #     initial = psutil.disk_io_counters()
    #     time.sleep(1)
    #     final = psutil.disk_io_counters()
    #     read_bytes = final.read_bytes - initial.read_bytes
    #     write_bytes = final.write_bytes - initial.write_bytes
    #     read_count = final.read_count - initial.read_count
    #     write_count = final.write_count - initial.write_count
    #     read_time = final.read_time - initial.read_time
    #     write_time = final.write_time - initial.write_time
    #
    #     # Calculate IOPS
    #     total_iops = read_count + write_count
    #
    #     return {'cpu_count': cpu_count,
    #             'cpu_user_times': cpu_user_times,
    #             'cpu_system_times': cpu_system_times,
    #             'cpu_idle_times': cpu_idle_times,
    #             'cpu_iowait_times': cpu_iowait_times,
    #             'cpu_irq_times': cpu_irq_times,
    #             'load_avg_1_min': round(load_avg[0], 2),
    #             'load_avg_5_min': round(load_avg[1], 2),
    #             'load_avg_15_min': round(load_avg[2], 2),
    #             'memory_info_rss': round(memory_info_rss, 2),
    #             'memory_info_vms': round(memory_info_vms, 2),
    #             'memory_info_shared': round(memory_info_shared, 2),
    #             'memory_info_text': round(memory_info_text, 2),
    #             'memory_info_data': round(memory_info_data, 2),
    #             'total_memory': round(total_memory, 2),
    #             'used_memory': round(used_mem, 2),
    #             'free_memory': round(free_mem, 2),
    #             'cached_memory': round(cached_memory, 2),
    #             'buffered_memory': round(buffered_memory, 2),
    #             'shared_memory': round(shared_memory, 2),
    #             'read_bytes': round(read_bytes, 2),
    #             'write_bytes': round(write_bytes, 2),
    #             'read_time': round(read_time, 2),
    #             'write_time': round(write_time, 2),
    #             'total_iops': round(total_iops, 2),
    #             'read_count': round(read_count, 2),
    #             'write_count': round(write_count, 2),
    #             'allowed_workers': allowed_workers,
    #             'current_workers': current_workers,
    #             'min_cpu_count': min_cpu_count}

    @api.model
    def get_system_metrics_data(self):
        """Get CPU, Server, and disk performance usage"""

        # cpu utilization
        cpu_count = psutil.cpu_count(logical=True)
        threshold_good = 0.7 * cpu_count

        cpu_times = psutil.cpu_times_percent(interval=1)
        cpu_user_times = cpu_times.user
        cpu_system_times = cpu_times.system
        cpu_idle_times = cpu_times.idle
        cpu_iowait_times = cpu_times.iowait
        cpu_irq_times = cpu_times.irq
        load_avg = psutil.getloadavg()
        cpu_freq = psutil.cpu_freq()

        allowed_workers = (cpu_count * 2) + 1
        current_workers = tools.config['workers']
        min_cpu_count = (current_workers - 1) / 2

        def grade_cpu_user_time(cpu_user_times):
            """ensure the grade for cpu user time"""

            if cpu_user_times < 50:
                return 4
            elif 50 <= cpu_user_times <= 70:
                return 3
            else:
                return 2

        def grade_cpu_system_time(cpu_system_times):
            """ensure the grade for cpu system times"""

            if cpu_system_times < 30:
                return 4
            elif 30 <= cpu_system_times <= 50:
                return 3
            else:
                return 2

        def grade_cpu_idle_times(cpu_idle_times):
            """ensure the grade for cpu idle times"""

            if cpu_idle_times >= 50:
                return 4
            elif 30 <= cpu_idle_times < 50:
                return 3
            else:
                return 2

        def grade_cpu_iowait_times(cpu_iowait_times):
            """ensure the grade for cpu iowait times"""

            if cpu_iowait_times < 10:
                return 4
            elif 10 <= cpu_iowait_times < 20:
                return 3
            else:
                return 2

        def grade_cpu_count(current_workers, allowed_workers):
            """ensure the grade for cpu count"""

            if current_workers < allowed_workers:
                return 4
            elif current_workers > allowed_workers:
                return 3
            else:
                return 2

        def grade_cpu_loadavg(load_avg, threshold_good, cpu_count):
            """ensure the grade for cpu load averages"""

            results = []
            for load in load_avg:
                if load <= threshold_good:
                    results.append(4)
                elif threshold_good < load <= cpu_count:
                    results.append(3)
                else:
                    results.append(2)
            return sum(results)

        def overall_cpu_grade(cpu_data):
            """ get overall cpu grade"""

            cpu_user_times = cpu_data.get('cpu_user_times', 0)
            cpu_system_times = cpu_data.get('cpu_system_times', 0)
            cpu_idle_times = cpu_data.get('cpu_idle_times', 0)
            cpu_iowait_times = cpu_data.get('cpu_iowait_times', 0)
            load_avg = cpu_data.get('load_avg', 0)
            threshold_good = cpu_data.get('threshold_good', 0)
            cpu_count = cpu_data.get('cpu_count', 0)
            allowed_workers = cpu_data.get('allowed_workers', 0)
            current_workers = cpu_data.get('current_workers', 0)

            grades = [
                grade_cpu_user_time(cpu_user_times),
                grade_cpu_system_time(cpu_system_times),
                grade_cpu_idle_times(cpu_idle_times),
                grade_cpu_iowait_times(cpu_iowait_times),
                grade_cpu_count(current_workers,allowed_workers),
                grade_cpu_loadavg(load_avg, threshold_good, cpu_count)

            ]
            overall_score = sum(grades)
            if overall_score >= 28.8: #80% of 12
                return "A"
            elif overall_score >= 25.6: #60%
                return "B"
            elif overall_score >= 22.4:
                return "C"
            else:
                return "D"

        cpu_data = {
            'cpu_user_times': cpu_user_times,
            'cpu_system_times': cpu_system_times,
            'cpu_idle_times': cpu_idle_times,
            'cpu_iowait_times': cpu_iowait_times,
            'threshold_good': threshold_good,
            'cpu_count': cpu_count,
            'load_avg': load_avg,
            'allowed_workers': allowed_workers,
            'current_workers': current_workers,
        }
        cpu_grade = overall_cpu_grade(cpu_data)

        return {
            'cpu_count': cpu_count,
            'cpu_user_times': cpu_user_times,
            'cpu_system_times': cpu_system_times,
            'cpu_idle_times': cpu_idle_times,
            'cpu_iowait_times': cpu_iowait_times,
            'cpu_irq_times': cpu_irq_times,
            'load_avg_1_min': round(load_avg[0], 2),
            'load_avg_5_min': round(load_avg[1], 2),
            'load_avg_15_min': round(load_avg[2], 2),
            'cpu_freq_current': round(cpu_freq.current, 2),
            'cpu_freq_max': round(cpu_freq.max, 2),
            'cpu_freq_min': round(cpu_freq.min, 2),
            'allowed_workers': allowed_workers,
            'current_workers': current_workers,
            'min_cpu_count': min_cpu_count,
            'cpu_grade': cpu_grade,
            'threshold_good': threshold_good
        }

    @api.model
    def get_memory_metrics_data(self):
        """get memory metrics data"""

        memory = psutil.virtual_memory()
        total_memory = memory.total / (1024.0 ** 2)
        cached_memory = (memory.cached / (1024 ** 2))
        buffered_memory = (memory.buffers / (1024 ** 2))
        shared_memory = (memory.shared / (1024 ** 2))
        used_ram_percent = memory.percent  # memory usage
        total_ram = round(memory.total / (1024.0 ** 2), 2)  # total memory
        used_mem = (total_ram * used_ram_percent) / 100
        free_mem = total_ram - used_mem

        def grade_used_memory(used_mem, total_memory):
            """ensure the grade for cpu count"""
            print("used",used_mem)
            print("total",total_memory)
            if used_mem <= (0.8 * total_memory):
                return 4
            elif used_mem > (0.8 * total_memory) and used_mem <= (0.9 * total_memory):
                return 3
            else:
                return 2

        def grade_free_memory(free_mem, total_memory):
            """ensure the grade for cpu count"""
            print("free",free_mem)
            if free_mem >= (0.2 * total_memory):
                return 4
            elif free_mem > (0.1 * total_memory) and free_mem < (0.2 * total_memory):
                return 3
            else:
                return 2

        def grade_shared_memory(shared_memory, total_memory):
            """ensure the grade for cpu count"""
            print("free", free_mem)
            if shared_memory < (0.25 * total_memory):
                return 4
            elif shared_memory >= (0.25 * total_memory) and shared_memory <= (0.5 * total_memory):
                return 3
            else:
                return 2

        def grade_cached_memory(cached_memory, total_memory):
            """ensure the grade for cpu count"""
            if cached_memory < (0.5 * total_memory):
                return 4
            elif cached_memory >= (0.5 * total_memory) and cached_memory <= (0.75 * total_memory):
                return 3
            else:
                return 2

        def grade_buffered_memory(buffered_memory, total_memory):
            """ensure the grade for cpu count"""
            if buffered_memory < (0.5 * total_memory):
                return 4
            elif cached_memory >= (0.5 * total_memory) and cached_memory <= (0.75 * total_memory):
                return 3
            else:
                return 2


        def overall_cpu_grade(cpu_data):
            """ get overall cpu grade"""

            free_mem = cpu_data.get('free_memory', 0)
            used_mem = cpu_data.get('used_memory', 0)
            shared_memory = cpu_data.get('shared_memory', 0)
            cached_memory = cpu_data.get('cached_memory', 0)
            buffered_memory = cpu_data.get('buffered_memory', 0)

            grades = [
                grade_free_memory(free_mem, total_memory),
                grade_used_memory(used_mem, total_memory),
                grade_shared_memory(shared_memory, total_memory),
                grade_cached_memory(cached_memory, total_memory),
                grade_buffered_memory(buffered_memory, total_memory)

            ]
            overall_score = sum(grades)
            print("overall_score",overall_score)
            if overall_score >= 18:  # 90% of 20
                return "A"
            elif overall_score >= 16:  # 80%
                return "B"
            elif overall_score >= 14:  #90%
                return "C"
            else:
                return "D"

        cpu_data = {
            'free_memory': free_mem,
            'used_memory': used_mem,
            'total_memory': total_memory,
            'shared_memory': shared_memory,
            'cached_memory': cached_memory,
            'buffered_memory': buffered_memory,
            }
        cpu_grade = overall_cpu_grade(cpu_data)
        return {'total_memory': round(total_memory, 2),
            'used_memory': round(used_mem, 2),
            'free_memory': round(free_mem, 2),
            'cached_memory': round(cached_memory, 2),
            'buffered_memory': round(buffered_memory, 2),
            'shared_memory': round(shared_memory, 2),
            'cpu_grade': cpu_grade}

    @api.model
    def get_process_memory_metrics_data(self):
        """get memory metrics data"""

        pid = os.getpid()
        process = psutil.Process(pid)

        # Get Memory Usage
        memory = psutil.virtual_memory()
        total_memory = memory.total / (1024.0 ** 2)
        memory_info = process.memory_info()
        memory_info_rss = (memory_info.rss / (1024 ** 2))
        memory_info_vms = (memory_info.vms / (1024 ** 2))
        memory_info_shared = (memory_info.shared / (1024 ** 2))
        memory_info_text = (memory_info.text / (1024 ** 2))
        memory_info_data = (memory_info.data / (1024 ** 2))

        def grade_process_memory(memory_info_rss, total_memory):
            """ensure the grade for process resident memory"""
            print("memory_info_rss",memory_info_rss)
            if memory_info_rss <= (0.25 * total_memory):
                return 4
            elif memory_info_rss > (0.25 * total_memory) and memory_info_rss <= (0.5 * total_memory):
                return 3
            else:
                return 2

        def grade_vms_memory(memory_info_vms, memory_info_rss):
            """ensure the grade for virtual memory size"""
            print("memory_info_vms", memory_info_vms)
            if memory_info_vms <= (3 * memory_info_rss):
                return 4
            elif memory_info_vms > (3 * memory_info_rss) and memory_info_rss <= (5 * memory_info_rss):
                return 3
            else:
                return 2

        def grade_shared_memory(memory_info_shared):
            """ensure the grade for virtual memory size"""
            print("memory_info_shared", memory_info_shared)
            if memory_info_shared <= 50:
                return 4
            elif memory_info_shared > 50 and memory_info_shared <= 200:
                return 3
            else:
                return 2

        def grade_text_memory(memory_info_text):
            """ensure the grade for virtual memory size"""
            print("memory_info_text", memory_info_text)
            if memory_info_text <= 10:
                return 4
            elif memory_info_text > 10 and memory_info_shared <= 50:
                return 3
            else:
                return 2

        def grade_data_memory(memory_info_data):
            """ensure the grade for virtual memory size"""
            print("memory_info_data", memory_info_data)
            if memory_info_text <= 200:
                return 4
            elif memory_info_text > 200 and memory_info_shared <= 500:
                return 3
            else:
                return 2

        def overall_cpu_grade(cpu_data):
            """ get overall cpu grade"""

            memory_info_rss = cpu_data.get('memory_info_rss', 0)
            memory_info_vms = cpu_data.get('memory_info_vms', 0)
            memory_info_shared = cpu_data.get('memory_info_shared', 0)
            memory_info_text = cpu_data.get('memory_info_text', 0)
            memory_info_data = cpu_data.get('memory_info_data', 0)

            grades = [
                grade_process_memory(memory_info_rss, total_memory),
                grade_vms_memory(memory_info_vms, total_memory),
                grade_shared_memory(memory_info_shared),
                grade_text_memory(memory_info_text),
                grade_data_memory(memory_info_data)
            ]
            overall_score = sum(grades)
            if overall_score >= 28.8:  # 80% of 12
                return "A"
            elif overall_score >= 25.6:  # 60%
                return "B"
            elif overall_score >= 22.4:
                return "C"
            else:
                return "D"

        cpu_data = {'memory_info_rss': memory_info_rss,
                    'memory_info_vms': memory_info_vms,
                    'memory_info_shared': memory_info_shared,
                    'memory_info_text': memory_info_text,
                    'memory_info_data': memory_info_data}

        cpu_grade = overall_cpu_grade(cpu_data)

        return {'memory_info_rss': round(memory_info_rss, 2),
            'memory_info_vms': round(memory_info_vms, 2),
            'memory_info_shared': round(memory_info_shared, 2),
            'memory_info_text': round(memory_info_text, 2),
            'memory_info_data': round(memory_info_data, 2),
            'total_memory': total_memory}

    @api.model
    def get_disk_metrics_data(self):
        """get memory metrics data"""

        # Disk performance
        initial = psutil.disk_io_counters()
        time.sleep(1)
        final = psutil.disk_io_counters()
        read_bytes = final.read_bytes - initial.read_bytes
        write_bytes = final.write_bytes - initial.write_bytes
        read_count = final.read_count - initial.read_count
        write_count = final.write_count - initial.write_count
        read_time = final.read_time - initial.read_time
        write_time = final.write_time - initial.write_time

        # Calculate IOPS
        total_iops = read_count + write_count

        return {'read_bytes': round(read_bytes, 2),
                'write_bytes': round(write_bytes, 2),
                'read_time': round(read_time, 2),
                'write_time': round(write_time, 2),
                'total_iops': round(total_iops, 2),
                'read_count': round(read_count, 2),
                'write_count': round(write_count, 2)}


    @api.model
    def get_server_uptime(self):
        """Get the server uptime."""

        result = subprocess.run(['uptime', '-p'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        uptime = result.stdout.decode('utf-8').strip()
        return {'uptime': uptime}

    @api.model
    def get_odoo_edition_info(self):
        is_enterprise = bool(get_module_path('web_enterprise'))

        if not is_enterprise:
            print("✅ This is the Community edition of Odoo.")
            return {
                'edition': 'Community',
                'expiration_date': None,
                'expiration_reason': None,
                'uuid': None,
                'message': '✅ This is the Community edition of Odoo.'
            }

        config = self.env['ir.config_parameter'].sudo()
        create_date = config.get_param('database.create_date')
        expiration_date = config.get_param('database.expiration_date')
        if (expiration_date == False):
            end_date = "This database will expire in 1 month."
        else:
            end_date = expiration_date

        print("✅ This is the Enterprise edition of Odoo.")
        print("📅 Create Date: %s", create_date)
        print("📅 Expiration Date: %s", end_date)

        return {
            'edition': 'Enterprise',
            'expiration_date': create_date,
            'Create_date': create_date,
            'message': '✅ This is the Enterprise edition of Odoo.'
        }
