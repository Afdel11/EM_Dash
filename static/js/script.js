// Graphique Supplémentaire 1
var ctx3 = document.getElementById('additional-chart-1').getContext('2d');
var chart3 = new Chart(ctx3, {
    type: 'bar',
    data: {
        labels: ['January', 'February', 'March', 'April'],
        datasets: [{
            label: 'Additional Chart 1',
            data: [150, 250, 350, 450],
            backgroundColor: 'rgba(255, 111, 97, 0.2)',
            borderColor: 'rgba(255, 111, 97, 1)',
            borderWidth: 2
        }]
    }
});

// Graphique Supplémentaire 2
var ctx4 = document.getElementById('additional-chart-2').getContext('2d');
var chart4 = new Chart(ctx4, {
    type: 'pie',
    data: {
        labels: ['Item 1', 'Item 2', 'Item 3'],
        datasets: [{
            label: 'Additional Chart 2',
            data: [120, 150, 100],
            backgroundColor: ['#ff6f61', '#00bfa5', '#ffcc00'],
        }]
    }
});
