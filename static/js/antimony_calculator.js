document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('calculatorForm');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Собираем данные формы
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Отправляем AJAX запрос
        try {
            const response = await fetch('/antimony/calculate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            
            if (result.success) {
                displayResults(result);
            } else {
                showError(result.error);
            }
            
        } catch (error) {
            console.error('Error:', error);
            showError('Ошибка сети при выполнении расчета');
        }
    });
});

function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    const noResults = document.getElementById('noResults');
    
    // Показываем контейнер результатов
    noResults.classList.add('hidden');
    resultsContainer.classList.remove('hidden');
    
    // Формируем HTML результатов
    resultsContainer.innerHTML = `
        <!-- Основные показатели -->
        <div class="space-y-4">
            <h3 class="text-lg font-semibold text-yellow-400 border-b border-yellow-400/30 pb-2">
                🏆 Черновая сурьма
            </h3>
            
            <div class="grid grid-cols-2 gap-4">
                <div class="bg-gradient-to-br from-green-500/10 to-green-600/10 border border-green-500/30 rounded-xl p-4">
                    <div class="text-green-400 text-3xl font-bold mb-1">
                        ${data.crude_antimony.mass} г
                    </div>
                    <div class="text-gray-400 text-sm">
                        Масса (${data.crude_antimony.yield_percent}% от шихты)
                    </div>
                </div>
                
                <div class="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/30 rounded-xl p-4">
                    <div class="text-blue-400 text-3xl font-bold mb-1">
                        ${data.crude_antimony.sb_content}%
                    </div>
                    <div class="text-gray-400 text-sm">
                        Содержание Sb
                    </div>
                </div>
            </div>
            
            <div class="bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/30 rounded-xl p-4">
                <div class="flex justify-between items-center">
                    <span class="text-gray-300">Извлечение Sb:</span>
                    <span class="text-purple-400 text-2xl font-bold">
                        ${data.crude_antimony.sb_extraction}%
                    </span>
                </div>
                <div class="mt-2 bg-gray-700/50 rounded-full h-3 overflow-hidden">
                    <div class="bg-gradient-to-r from-purple-500 to-purple-600 h-full transition-all duration-1000" 
                         style="width: ${data.crude_antimony.sb_extraction}%"></div>
                </div>
            </div>
            
            <!-- Примеси -->
            <div class="bg-white/5 rounded-xl p-4 space-y-2">
                <h4 class="text-sm font-medium text-gray-400 mb-3">Состав примесей:</h4>
                <div class="grid grid-cols-2 gap-3 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-400">Na:</span>
                        <span class="text-white font-medium">${data.crude_antimony.impurities.na}%</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">As:</span>
                        <span class="text-white font-medium">${data.crude_antimony.impurities.as}%</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">Pb:</span>
                        <span class="text-white font-medium">${data.crude_antimony.impurities.pb}%</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">Fe:</span>
                        <span class="text-white font-medium">${data.crude_antimony.impurities.fe}%</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Шлак -->
        <div class="space-y-4">
            <h3 class="text-lg font-semibold text-yellow-400 border-b border-yellow-400/30 pb-2">
                🗑️ Шлак
            </h3>
            
            <div class="grid grid-cols-2 gap-4">
                <div class="bg-white/5 rounded-xl p-4">
                    <div class="text-gray-400 text-sm mb-1">Масса шлака</div>
                    <div class="text-white text-2xl font-bold">
                        ${data.slag.mass} г
                    </div>
                    <div class="text-gray-500 text-xs mt-1">
                        (${data.slag.yield_percent}% от шихты)
                    </div>
                </div>
                
                <div class="bg-white/5 rounded-xl p-4">
                    <div class="text-gray-400 text-sm mb-1">Потери Sb в шлаке</div>
                    <div class="text-red-400 text-2xl font-bold">
                        ${data.slag.sb_losses} г
                    </div>
                    <div class="text-gray-500 text-xs mt-1">
                        (${data.slag.sb_content}% Sb в шлаке)
                    </div>
                </div>
            </div>
            
            <div class="bg-white/5 rounded-xl p-4">
                <div class="flex justify-between text-sm">
                    <span class="text-gray-400">Содержание Na в шлаке:</span>
                    <span class="text-white font-medium">${data.slag.na_content}%</span>
                </div>
            </div>
        </div>
        
        <!-- Потери -->
        <div class="space-y-4">
            <h3 class="text-lg font-semibold text-yellow-400 border-b border-yellow-400/30 pb-2">
                💨 Потери в газовую фазу
            </h3>
            
            <div class="space-y-3">
                <div class="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                    <div class="flex justify-between items-center">
                        <span class="text-gray-300">Sb в газы:</span>
                        <span class="text-red-400 font-bold">${data.losses.sb_to_gas} г</span>
                    </div>
                </div>
                
                <div class="bg-orange-500/10 border border-orange-500/30 rounded-xl p-4">
                    <div class="flex justify-between items-center">
                        <span class="text-gray-300">As в газы:</span>
                        <span class="text-orange-400 font-bold">${data.losses.as_to_gas} г</span>
                    </div>
                </div>
                
                <div class="bg-white/5 rounded-xl p-4">
                    <div class="flex justify-between items-center">
                        <span class="text-gray-300">Общие потери:</span>
                        <span class="text-white font-bold">
                            ${data.losses.total_losses_percent}%
                        </span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Материальный баланс -->
        <div class="space-y-4">
            <h3 class="text-lg font-semibold text-yellow-400 border-b border-yellow-400/30 pb-2">
                ⚖️ Материальный баланс
            </h3>
            
            <!-- Баланс по Sb -->
            <div class="bg-white/5 rounded-xl p-4 space-y-3">
                <h4 class="text-sm font-medium text-gray-300">Сурьма (Sb):</h4>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-400">Загружено:</span>
                        <span class="text-white font-medium">${data.balance.sb.loaded} г</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">→ В черновую сурьму:</span>
                        <span class="text-green-400 font-medium">${data.balance.sb.to_crude} г</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">→ В шлак:</span>
                        <span class="text-yellow-400 font-medium">${data.balance.sb.to_slag} г</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">→ В газы:</span>
                        <span class="text-red-400 font-medium">${data.balance.sb.to_gas} г</span>
                    </div>
                    <div class="border-t border-white/10 pt-2 flex justify-between font-semibold">
                        <span class="text-gray-300">Извлечение:</span>
                        <span class="text-purple-400">${data.balance.sb.extraction_percent}%</span>
                    </div>
                </div>
            </div>
            
            <!-- Баланс по Na -->
            <div class="bg-white/5 rounded-xl p-4 space-y-3">
                <h4 class="text-sm font-medium text-gray-300">Натрий (Na):</h4>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-400">Загружено:</span>
                        <span class="text-white font-medium">${data.balance.na.loaded} г</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">→ В черновую сурьму:</span>
                        <span class="text-yellow-400 font-medium">${data.balance.na.to_crude} г</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">→ В шлак:</span>
                        <span class="text-green-400 font-medium">${data.balance.na.to_slag} г</span>
                    </div>
                </div>
            </div>
            
            <!-- Баланс по As -->
            <div class="bg-white/5 rounded-xl p-4 space-y-3">
                <h4 class="text-sm font-medium text-gray-300">Мышьяк (As):</h4>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-400">Загружено:</span>
                        <span class="text-white font-medium">${data.balance.as.loaded} г</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">→ В черновую сурьму:</span>
                        <span class="text-blue-400 font-medium">${data.balance.as.to_crude} г</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">→ В шлак:</span>
                        <span class="text-yellow-400 font-medium">${data.balance.as.to_slag} г</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">→ В газы:</span>
                        <span class="text-red-400 font-medium">${data.balance.as.to_gas} г</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Рекомендации -->
        ${generateRecommendationsHTML(data.recommendations)}
        
        <!-- Исходные данные (сводка) -->
        <div class="bg-white/5 rounded-xl p-4 space-y-2 text-sm">
            <h4 class="text-gray-300 font-medium mb-3">📋 Условия плавки:</h4>
            <div class="grid grid-cols-2 gap-2 text-xs">
                <div><span class="text-gray-500">Антимонат:</span> <span class="text-white">${data.input.antimonite_mass} г</span></div>
                <div><span class="text-gray-500">Сухой вес:</span> <span class="text-white">${data.input.dry_antimonite} г</span></div>
                <div><span class="text-gray-500">Температура:</span> <span class="text-white">${data.input.temperature}°C</span></div>
                <div><span class="text-gray-500">Восстановитель:</span> <span class="text-white">${data.input.reducer_type_display}</span></div>
                <div><span class="text-gray-500">Расход восст.:</span> <span class="text-white">${data.input.reducer_amount}%</span></div>
                <div><span class="text-gray-500">Масса восст.:</span> <span class="text-white">${data.input.reducer_mass} г</span></div>
                <div><span class="text-gray-500">Общая шихта:</span> <span class="text-white">${data.input.total_charge} г</span></div>
                <div><span class="text-gray-500">Добавка Pb:</span> <span class="text-white">${data.input.lead_addition} г</span></div>
            </div>
        </div>
        
        <!-- Кнопки действий -->
        <div class="flex gap-4">
            <button onclick="window.print()" 
                    class="flex-1 py-3 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-xl transition">
                🖨️ Печать
            </button>
            <button onclick="copyResults()" 
                    class="flex-1 py-3 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-xl transition">
                📋 Копировать
            </button>
        </div>
    `;
    
    // Анимация появления
    resultsContainer.style.opacity = '0';
    setTimeout(() => {
        resultsContainer.style.transition = 'opacity 0.5s ease';
        resultsContainer.style.opacity = '1';
    }, 100);
}

function generateRecommendationsHTML(recommendations) {
    if (!recommendations || recommendations.length === 0) {
        return '';
    }
    
    const typeColors = {
        'success': 'from-green-500/10 to-green-600/10 border-green-500/30',
        'info': 'from-blue-500/10 to-blue-600/10 border-blue-500/30',
        'warning': 'from-yellow-500/10 to-yellow-600/10 border-yellow-500/30',
        'error': 'from-red-500/10 to-red-600/10 border-red-500/30'
    };
    
    const typeIcons = {
        'success': '✅',
        'info': 'ℹ️',
        'warning': '⚠️',
        'error': '❌'
    };
    
    let html = `
        <div class="space-y-4">
            <h3 class="text-lg font-semibold text-yellow-400 border-b border-yellow-400/30 pb-2">
                💡 Рекомендации и оценка
            </h3>
    `;
    
    recommendations.forEach(rec => {
        html += `
            <div class="bg-gradient-to-br ${typeColors[rec.type]} border rounded-xl p-4">
                <div class="flex items-start gap-3">
                    <span class="text-2xl">${typeIcons[rec.type]}</span>
                    <div class="flex-1">
                        <h4 class="font-semibold text-white mb-1">${rec.title}</h4>
                        <p class="text-gray-300 text-sm">${rec.text}</p>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    
    return html;
}

function showError(message) {
    const resultsContainer = document.getElementById('resultsContainer');
    const noResults = document.getElementById('noResults');
    
    noResults.classList.add('hidden');
    resultsContainer.classList.remove('hidden');
    
    resultsContainer.innerHTML = `
        <div class="bg-red-500/10 border border-red-500/30 rounded-xl p-6 text-center">
            <div class="text-6xl mb-4">❌</div>
            <h3 class="text-xl font-semibold text-red-400 mb-2">Ошибка расчета</h3>
            <p class="text-gray-300">${message}</p>
        </div>
    `;
}

function copyResults() {
    // Простая функция копирования результатов в текстовом виде
    const resultsContainer = document.getElementById('resultsContainer');
    const text = resultsContainer.innerText;
    
    navigator.clipboard.writeText(text).then(() => {
        alert('✅ Результаты скопированы в буфер обмена');
    }).catch(() => {
        alert('❌ Ошибка копирования');
    });
}

function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}