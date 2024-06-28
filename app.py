from flask import Flask, jsonify, request, send_file, render_template
from flask_socketio import SocketIO
from repository.database import db
from db_models.payment import Payment
from datetime import datetime, timedelta
from payments.pix import Pix

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///payments.db"
app.config["SECRET_KEY"] = "SECRET_KEY_WEBSOCKET"
socketio = SocketIO(app)

db.init_app(app)

@app.route("/payments/pix", methods=["POST"])
def create_payment_pix():
    data = request.get_json()
    if "value" not in data:
        return jsonify({"error": "Missing 'value' field."}), 400

    expiration_date = datetime.now() + timedelta(minutes=30)

    new_payment = Payment(value=data["value"], expiration_date=expiration_date)
    pix_obj = Pix()
    data_payment_pix = pix_obj.create_payment()

    new_payment.bank_payment_id = data_payment_pix["bank_payment_id"]
    new_payment.qr_code = data_payment_pix["qr_code_path"]

    db.session.add(new_payment)
    db.session.commit()

    return jsonify(
        {"message": "The payment has been created.", "payment": new_payment.to_dict()}
    )

@app.route("/payments/pix/qrcode/<file_name>", methods=["GET"])
def get_qrcode_image(file_name):
    return send_file(f"static/img/{file_name}.png", mimetype="image/png")


@app.route("/payments/pix/confirmation", methods=["POST`"])
def pix_confirmation():
    return jsonify({"message": "The payment has been confirmed."})


@app.route("/payments/pix/<int:payment_id>", methods=["GET"])
def payment_pix_page(payment_id):
    payment = Payment.query.get(payment_id)
    if payment is None:
        return render_template('404.html') 
    if payment.paid is True:
        return render_template('confirmed_payment.html', payment_id=payment.id, value=payment.value, host="http://127.0.0.1:5000", qr_code=payment.qr_code)
    return render_template('payment.html', payment_id=payment.id, value=payment.value, host="http://127.0.0.1:5000", qr_code=payment.qr_code)

# websocket section
@socketio.on("connect")
def handle_connection():
    print("Client connected")

if __name__ == "__main__":
    socketio.run(app, debug=True)
