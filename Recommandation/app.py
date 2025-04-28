from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Charger les données
df_sales = pd.read_pickle('rec.pkl')

# Grouper les ventes par Shop et Produit
df_grouped = df_sales.groupby(
    ['Shop_Fk', 'Product_Fk', 'Product_Name', 'Category'],
    as_index=False
).agg({
    'Product_Quantity_Sold': 'sum',
    'Total_General': 'sum'
})


# Générer les recommandations
def recommend_top_products_all(df_grouped, top_n=5):
    recommendations = {}
    for shop in df_grouped['Shop_Fk'].unique():
        df_shop = df_grouped[df_grouped['Shop_Fk'] == shop]
        top_products = df_shop.sort_values(by='Product_Quantity_Sold', ascending=False).head(top_n)
        recommendations[shop] = top_products
    return recommendations

# Liste des shops uniques pour la dropdown
shop_ids = sorted(df_grouped['Shop_Fk'].unique())

# Lancer les recommandations une fois
all_recommendations = recommend_top_products_all(df_grouped)

@app.route('/', methods=['GET', 'POST'])
def index():
    products = []
    selected_shop_id = None
    error = None

    if request.method == 'POST':
        try:
            selected_shop_id = int(request.form['shop_id'])
            if selected_shop_id in all_recommendations:
                products = all_recommendations[selected_shop_id].to_dict(orient='records')
            else:
                error = "Aucune donnée trouvée pour ce Shop."
        except ValueError:
            error = "ID de Shop invalide."

    return render_template(
        'index.html',
        shop_ids=shop_ids,
        products=products,
        error=error,
        shop_id=selected_shop_id,
        selected_shop_id=selected_shop_id
    )

if __name__ == '__main__':
    app.run(debug=True)
