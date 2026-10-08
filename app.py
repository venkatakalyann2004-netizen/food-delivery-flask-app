from flask import Flask, render_template_string, request, jsonify
import sqlite3

app = import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# Database Setup (Menu & Orders Tables)
def init_db():
    conn = sqlite3.connect('food.db')
    cursor = conn.cursor()
    # Menu Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL
        )
    ''')
    # Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            address TEXT,
            items TEXT,
            total_price REAL
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM menu')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO menu (name, price) VALUES (?, ?)', [
            ('Chicken Biryani', 250.0),
            ('Paneer Butter Masala', 200.0),
            ('Butter Naan', 40.0),
            ('Cool Drink', 50.0)
        ])
    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Food Express - Real Fullstack App</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 15px; }
        h1 { color: #d9534f; text-align: center; }
        .card { background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
        .btn-add { background: #28a745; color: white; border: none; padding: 10px 15px; border-radius: 5px; font-weight: bold; }
        .cart-box { background: #fff; padding: 15px; border-radius: 8px; margin-top: 20px; border: 2px solid #d9534f; }
        input { width: 90%; padding: 10px; margin: 5px 0; border: 1px solid #ccc; border-radius: 4px; }
        .btn-order { width: 100%; background: #d9534f; color: white; border: none; padding: 12px; border-radius: 5px; font-weight: bold; font-size: 16px; margin-top: 10px; }
        .msg { color: green; font-weight: bold; text-align: center; display: none; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>🍕 Food Express</h1>
    <div id="status-msg" class="msg">✅ Added to Cart!</div>
    
    <h3>Menu Items</h3>
    {% for item in items %}
    <div class="card">
        <div>
            <strong>{{ item[1] }}</strong><br>
            <span>₹{{ item[2] }}</span>
        </div>
        <button type="button" class="btn-add" onclick="addItem('{{ item[1] }}', {{ item[2] }})">+ Add</button>
    </div>
    {% endfor %}

    <div class="cart-box">
        <h3>Your Order</h3>
        <ul id="items-list"></ul>
        <p style="font-size: 18px;"><strong>Total: ₹<span id="total-val">0</span></strong></p>
        
        <input type="text" id="cust-name" placeholder="Your Name"><br>
        <input type="text" id="cust-addr" placeholder="Delivery Address"><br>
        <button type="button" class="btn-order" onclick="placeOrder()">Place Order Now</button>
        <div id="order-success" style="color: #d9534f; font-weight: bold; text-align: center; margin-top: 10px;"></div>
    </div>

    <script>
        let grandTotal = 0;
        let orderItems = [];

        function addItem(itemName, itemPrice) {
            orderItems.push(itemName);
            grandTotal += itemPrice;
            
            document.getElementById('total-val').innerText = grandTotal;
            let ul = document.getElementById('items-list');
            let li = document.createElement('li');
            li.appendChild(document.createTextNode(itemName + " - ₹" + itemPrice));
            ul.appendChild(li);

            let msg = document.getElementById('status-msg');
            msg.style.display = 'block';
            setTimeout(() => { msg.style.display = 'none'; }, 1500);
        }

        function placeOrder() {
            let name = document.getElementById('cust-name').value;
            let addr = document.getElementById('cust-addr').value;
            
            if (!name || !addr || orderItems.length === 0) {
                document.getElementById('order-success').innerText = "⚠️ Please add items & details!";
                return;
            }

            // Backend API ki POST call pampadam
            fetch('/place_order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name,
                    address: addr,
                    items: orderItems.join(", "),
                    total: grandTotal
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('order-success').innerText = "🎉 Order #" + data.order_id + " Saved in Database for " + name + "!";
                }
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    conn = sqlite3.connect('food.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menu')
    items = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, items=items)

# Real Backend API Endpoint to Store Orders
@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.json
    conn = sqlite3.connect('food.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (customer_name, address, items, total_price)
        VALUES (?, ?, ?, ?)
    ''', (data['name'], data['address'], data['items'], data['total']))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return jsonify({'status': 'success', 'order_id': order_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
