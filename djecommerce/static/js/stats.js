

function create_product_piechart(chart_id, series){

    $('#'+chart_id).highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {
            text: 'Products in Categories'
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                    }
                }
            }
        },
        series: series
    });
}


function create_product_stackchart(chart_id, categories, series){

    $('#'+chart_id).highcharts({
        chart: {
            type: 'area'
        },
        title: {
            text: 'Products added'
        },
        xAxis: {
            allowDecimals: false,
            categories: categories
        },
        yAxis: {
            title: {
                text: 'Products count'
            },
            labels: {
                formatter: function () {
                    return this.value;
                }
            }
        },
        plotOptions: {
            area: {
                marker: {
                    enabled: false,
                    symbol: 'circle',
                    radius: 2,
                    states: {
                        hover: {
                            enabled: true
                        }
                    }
                }
            }
        },
        series: series
    });
}