// 全局变量
let autoRefreshInterval = null;
let currentRefreshInterval = 0;

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
    // 更新当前时间
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // 初始化日志
    refreshLogs();
    
    // 初始化定时任务状态
    refreshSchedulerStatus();
    setInterval(refreshSchedulerStatus, 30000);
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 设置默认值
    setDefaultValues();
    
    // 启动防闲置检查
    startAntiIdleCheck();
}

// 绑定事件监听器
function bindEventListeners() {
    // 自动刷新间隔变化
    document.getElementById('auto-refresh-interval').addEventListener('change', handleAutoRefreshChange);
    
    // 筛选器变化
    document.getElementById('log-date-filter').addEventListener('change', refreshLogs);
    document.getElementById('log-account-filter').addEventListener('change', refreshLogs);
    document.getElementById('log-status-filter').addEventListener('change', refreshLogs);
    
    // 模态框关闭时重置表单
    document.getElementById('addAccountModal').addEventListener('hidden.bs.modal', resetAccountForm);
    document.getElementById('addEmailModal').addEventListener('hidden.bs.modal', resetEmailForm);
    
    // 表单提交
    document.getElementById('addAccountForm').addEventListener('submit', handleAccountSubmit);
    document.getElementById('addEmailForm').addEventListener('submit', handleEmailSubmit);
}

// 设置默认值
function setDefaultValues() {
    // 设置默认日期为今天
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('log-date-filter').value = today;
    
    // 设置默认自动刷新间隔
    document.getElementById('auto-refresh-interval').value = '20';
    handleAutoRefreshChange();
}

// 更新当前时间
function updateCurrentTime() {
    const now = new Date();
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    };
    const timeString = now.toLocaleString('zh-CN', options);
    document.getElementById('current-time').textContent = timeString;
}

// 处理自动刷新间隔变化
function handleAutoRefreshChange() {
    const interval = parseInt(document.getElementById('auto-refresh-interval').value);
    
    // 清除现有定时器
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
    
    // 设置新的定时器
    if (interval > 0) {
        autoRefreshInterval = setInterval(refreshLogs, interval * 1000);
        currentRefreshInterval = interval;
        showToast(`日志自动刷新已设置为 ${interval} 秒`, 'info');
    } else {
        showToast('日志自动刷新已关闭', 'info');
    }
}

// 刷新日志
function refreshLogs() {
    const date = document.getElementById('log-date-filter').value;
    const accountId = document.getElementById('log-account-filter').value;
    const status = document.getElementById('log-status-filter').value;
    
    let url = '/api/logs?';
    const params = new URLSearchParams();
    
    if (date) params.append('date', date);
    if (accountId) params.append('account_id', accountId);
    if (status) params.append('status', status);
    
    url += params.toString();
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            renderLogs(data);
        })
        .catch(error => {
            console.error('刷新日志失败:', error);
            showToast('刷新日志失败', 'error');
        });
}

// 渲染日志
function renderLogs(logs) {
    const container = document.getElementById('logs-container');
    
    if (logs.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-inbox fa-3x mb-3"></i>
                <p>暂无日志记录</p>
            </div>
        `;
        return;
    }
    
    const logsHtml = logs.map(log => {
        const statusClass = log.status === 'success' ? 'success' : 'danger';
        const statusIcon = log.status === 'success' ? 'check-circle' : 'times-circle';
        const statusText = log.status === 'success' ? '成功' : '失败';
        const time = new Date(log.created_at).toLocaleString('zh-CN');
        
        return `
            <div class="log-entry alert alert-${statusClass} alert-dismissible fade show" role="alert">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fas fa-${statusIcon} me-2"></i>
                            <strong>${log.account_name || '未知账号'}</strong>
                            <span class="badge bg-${statusClass} ms-2">${statusText}</span>
                        </div>
                        <div class="text-muted small">
                            ${log.message || '无详细信息'}
                        </div>
                        ${log.details ? `
                            <details class="mt-2">
                                <summary class="small text-primary">查看详细信息</summary>
                                <pre class="mt-2 p-2 bg-light rounded small">${JSON.stringify(log.details, null, 2)}</pre>
                            </details>
                        ` : ''}
                    </div>
                    <div class="text-muted small ms-3">
                        ${time}
                    </div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }).join('');
    
    container.innerHTML = logsHtml;
    
    // 添加动画效果
    const logEntries = container.querySelectorAll('.log-entry');
    logEntries.forEach((entry, index) => {
        entry.style.animationDelay = `${index * 0.1}s`;
    });
}

// 清空日志
function clearLogs() {
    if (confirm('确定要清空日志吗？此操作不可恢复。')) {
        const date = document.getElementById('log-date-filter').value;
        
        fetch('/api/logs/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ date: date })
        })
        .then(response => response.json())
        .then(data => {
            showToast('日志已清空', 'success');
            refreshLogs();
        })
        .catch(error => {
            console.error('清空日志失败:', error);
            showToast('清空日志失败', 'error');
        });
    }
}

// 添加账号
function addAccount() {
    const form = document.getElementById('addAccountForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // 验证表单
    if (!data.name || !data.account || !data.password) {
        showToast('请填写所有必填字段', 'error');
        return;
    }
    
    fetch('/api/accounts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        showToast('账号添加成功', 'success');
        bootstrap.Modal.getInstance(document.getElementById('addAccountModal')).hide();
        location.reload();
    })
    .catch(error => {
        console.error('添加账号失败:', error);
        showToast('添加账号失败', 'error');
    });
}

// 登录单个账号
function loginAccount(accountId) {
    if (!confirm('确定要为这个账号执行登录吗？')) {
        return;
    }
    
    fetch(`/api/login/${accountId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        showToast('正在执行登录...', 'info');
        // 5秒后自动刷新日志
        setTimeout(refreshLogs, 5000);
    })
    .catch(error => {
        console.error('登录失败:', error);
        showToast('登录失败', 'error');
    });
}

// 登录所有账号
function loginAllAccounts() {
    if (!confirm('确定要为所有账号执行登录吗？这可能需要一些时间。')) {
        return;
    }
    
    fetch('/api/login/all', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        showToast('正在为所有账号执行登录...', 'info');
        // 10秒后自动刷新日志
        setTimeout(refreshLogs, 10000);
    })
    .catch(error => {
        console.error('登录失败:', error);
        showToast('登录失败', 'error');
    });
}

// 删除账号
function deleteAccount(accountId) {
    if (!confirm('确定要删除这个账号吗？此操作不可恢复。')) {
        return;
    }
    
    fetch(`/api/accounts/${accountId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            showToast('账号删除成功', 'success');
            location.reload();
        } else {
            throw new Error('删除失败');
        }
    })
    .catch(error => {
        console.error('删除账号失败:', error);
        showToast('删除账号失败', 'error');
    });
}

// 添加邮件配置
function addEmailConfig() {
    const form = document.getElementById('addEmailForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // 验证表单
    if (!data.smtp_server || !data.sender_email || !data.sender_password || !data.receiver_email) {
        showToast('请填写所有必填字段', 'error');
        return;
    }
    
    fetch('/api/email_configs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        showToast('邮件配置添加成功', 'success');
        bootstrap.Modal.getInstance(document.getElementById('addEmailModal')).hide();
        location.reload();
    })
    .catch(error => {
        console.error('添加邮件配置失败:', error);
        showToast('添加邮件配置失败', 'error');
    });
}

// 删除邮件配置
function deleteEmailConfig(configId) {
    if (!confirm('确定要删除这个邮件配置吗？此操作不可恢复。')) {
        return;
    }
    
    fetch(`/api/email_configs/${configId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            showToast('邮件配置删除成功', 'success');
            location.reload();
        } else {
            throw new Error('删除失败');
        }
    })
    .catch(error => {
        console.error('删除邮件配置失败:', error);
        showToast('删除邮件配置失败', 'error');
    });
}

// 刷新定时任务状态
function refreshSchedulerStatus() {
    fetch('/api/scheduler/status')
        .then(response => response.json())
        .then(data => {
            renderSchedulerStatus(data);
        })
        .catch(error => {
            console.error('刷新定时任务状态失败:', error);
        });
}

// 渲染定时任务状态
function renderSchedulerStatus(data) {
    const container = document.getElementById('scheduler-status');
    
    const statusBadge = data.running ? 
        '<span class="badge bg-success me-2"><i class="fas fa-play me-1"></i>运行中</span>' :
        '<span class="badge bg-danger me-2"><i class="fas fa-stop me-1"></i>已停止</span>';
    
    let jobsHtml = '<div class="mt-2">';
    if (data.jobs && data.jobs.length > 0) {
        data.jobs.forEach(job => {
            const nextRun = job.next_run ? new Date(job.next_run).toLocaleString('zh-CN') : '无';
            jobsHtml += `
                <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-light rounded">
                    <div>
                        <i class="fas fa-clock me-2 text-primary"></i>
                        <strong>${job.name}</strong>
                    </div>
                    <small class="text-muted">下次运行: ${nextRun}</small>
                </div>
            `;
        });
    } else {
        jobsHtml += '<div class="text-muted">暂无定时任务</div>';
    }
    jobsHtml += '</div>';
    
    container.innerHTML = statusBadge + jobsHtml;
}

// 手动执行定时任务
function runSchedulerJob() {
    if (!confirm('确定要手动执行定时任务吗？')) {
        return;
    }
    
    fetch('/api/scheduler/run', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        showToast('定时任务执行完成', 'success');
        refreshLogs();
        refreshSchedulerStatus();
    })
    .catch(error => {
        console.error('执行定时任务失败:', error);
        showToast('执行定时任务失败', 'error');
    });
}

// 显示提示消息
function showToast(message, type = 'info') {
    const toastEl = document.getElementById('liveToast');
    const toastMessage = document.getElementById('toast-message');
    
    // 设置消息内容
    toastMessage.textContent = message;
    
    // 设置样式
    toastEl.className = 'toast';
    if (type === 'success') {
        toastEl.classList.add('bg-success', 'text-white');
    } else if (type === 'error') {
        toastEl.classList.add('bg-danger', 'text-white');
    } else {
        toastEl.classList.add('bg-primary', 'text-white');
    }
    
    // 显示提示
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// 重置账号表单
function resetAccountForm() {
    document.getElementById('addAccountForm').reset();
}

// 重置邮件表单
function resetEmailForm() {
    document.getElementById('addEmailForm').reset();
}

// 处理账号表单提交
function handleAccountSubmit(event) {
    event.preventDefault();
    addAccount();
}

// 处理邮件表单提交
function handleEmailSubmit(event) {
    event.preventDefault();
    addEmailConfig();
}

// 启动防闲置检查
function startAntiIdleCheck() {
    // 每20秒发送一次健康检查请求
    setInterval(() => {
        fetch('/api/health')
            .then(response => response.json())
            .then(data => {
                console.log('Health check:', data);
            })
            .catch(error => {
                console.error('Health check failed:', error);
            });
    }, 20000);
}

// 工具函数：格式化时间
function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

// 工具函数：显示加载状态
function showLoading(element) {
    element.innerHTML = `
        <div class="text-center text-muted">
            <div class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            加载中...
        </div>
    `;
}

// 工具函数：显示错误状态
function showError(element, message) {
    element.innerHTML = `
        <div class="text-center text-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        </div>
    `;
}

// 工具函数：验证邮箱格式
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// 工具函数：防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 工具函数：节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}