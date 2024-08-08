document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');

    // Gráfico de Pizza para Agendamentos Confirmados, Cancelados e Em Trânsito
    const ctxConfirmed = document.getElementById('confirmedChart').getContext('2d');
    const confirmedChart = new Chart(ctxConfirmed, {
        type: 'pie',
        data: {
            labels: ['Confirmados', 'Cancelados', 'Em Trânsito'],
            datasets: [{
                data: [{{ confirmed_percentage }}, {{ canceled_percentage }}, {{ in_transit_percentage }}],
                backgroundColor: ['#4CAF50', '#FF0000', '#FFA500']
            }]
        },
        options: {
            responsive: true
        }
    });

    // Gráfico de Mapa de Agendamentos por Região (apenas exemplo, ajuste conforme necessário)
    const ctxRegion = document.getElementById('regionChart').getContext('2d');
    const regionChart = new Chart(ctxRegion, {
        type: 'bar',
        data: {
            labels: ['Região 1', 'Região 2', 'Região 3'], // Substitua com dados reais
            datasets: [{
                label: 'Agendamentos por Região',
                data: [10, 20, 30], // Substitua com dados reais
                backgroundColor: '#003366'
            }]
        },
        options: {
            responsive: true
        }
    });

    // Gráfico de Barras para Vagas em Aberto, Em Andamento e Finalizadas
    const ctxStatus = document.getElementById('statusChart').getContext('2d');
    const statusChart = new Chart(ctxStatus, {
        type: 'bar',
        data: {
            labels: ['Vagas em Aberto', 'Em Andamento', 'Finalizados'],
            datasets: [{
                label: 'Status das Vagas',
                data: [5, 10, 15], // Substitua com dados reais
                backgroundColor: ['#007bff', '#ffcc00', '#28a745']
            }]
        },
        options: {
            responsive: true
        }
    });
});

console.log({
    confirmed_percentage: {{ confirmed_percentage }},
    canceled_percentage: {{ canceled_percentage }},
    in_transit_percentage: {{ in_transit_percentage }}
});
