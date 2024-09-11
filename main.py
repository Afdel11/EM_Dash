from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def dashboard():
    data = {
        'orders': 12000,
        'tax_deduction': 5000,
        'revenue': 8000,
        'yearly_sales': 12000,
        'order_stats': 8500
    }
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
