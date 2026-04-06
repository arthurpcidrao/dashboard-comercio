import altair as alt

def plot_line_chart(df, x, y, color, x_label, y_label, title):
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X(f'{x}:T', title=x_label),
        y=alt.Y(f'{y}:Q', title=y_label),
        color=alt.Color(f'{color}:N', legend=alt.Legend(title="Categoria")),
        tooltip=[x, y, color]
    ).properties(title=title, height=400).interactive()
    return chart

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
