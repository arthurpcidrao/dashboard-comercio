import altair as alt

def plot_line_chart(df, x, y, color, x_label, y_label, title):
    # Base do gráfico de linha
    base = alt.Chart(df).encode(
        x=alt.X(f'{x}:T', title=x_label),
        y=alt.Y(f'{y}:Q', title=y_label)
    )
    
    # Criamos a linha principal com pontos
    line = base.mark_line(point=True).encode(
        tooltip=[alt.Tooltip(f'{x}:T', title=x_label), 
                 alt.Tooltip(f'{y}:Q', title=y_label, format=".2f")]
    )

    # Lógica de Cor e Linha de Tendência
    if color and df[color].nunique() > 1:
        # Se tiver mais de uma categoria, aplica cores e legendas normalmente
        chart = line.encode(
            color=alt.Color(f'{color}:N', legend=alt.Legend(title="Legenda")),
            tooltip=[f'{x}:T', f'{y}:Q', f'{color}:N']
        )
    else:
        # Se tiver apenas 1 cor ou nenhuma, adicionamos a linha de tendência
        trend = base.transform_regression(x, y).mark_line(
            color='red', 
            strokeDash=[5, 5],
            opacity=0.7
        )
        
        # Combinamos a linha de dados com a linha de tendência (Layering)
        chart = alt.layer(line, trend)

    return chart.properties(title=title, height=400).interactive()


def plot_bar_chart(df, x, y, x_label, y_label, title):
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f'{x}:Q', title=x_label),
        y=alt.Y(f'{y}:N', sort='-x', title=y_label),
        color=alt.value("#0068c9"),
        tooltip=[x, y]
    ).properties(title=title, height=400)
    return chart


def plot_heatmap(df, x, y, color, x_label, y_label, title):
    chart = alt.Chart(df).mark_rect().encode(
        x=alt.X(f'{x}:O', title=x_label),
        y=alt.Y(f'{y}:O', title=y_label),
        color=alt.Color(f'{color}:Q', scale=alt.Scale(scheme='viridis'), title="Valor"),
        tooltip=[x, y, color]
    ).properties(title=title, height=400)
    return chart


def plot_donut_chart(df, theta, color, title):
    chart = alt.Chart(df).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field=theta, type="quantitative"),
        color=alt.Color(field=color, type="nominal", legend=alt.Legend(title="Status")),
        tooltip=[color, theta]
    ).properties(title=title, height=300)
    return chart