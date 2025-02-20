from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from flask import request, render_template
from flask_login import current_user
from flask import Flask, jsonify, request, render_template


# Inicializa o app
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///motel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

    
#=====================================================================================#

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar seu perfil.', 'warning')
        return redirect(url_for('login'))  # Redirecionar para a página de login se não estiver logado

    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    
    # Exibir perfil do usuário
    return render_template('profile.html', user=user)

# Rota para editar o perfil do usuário
@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Por favor, faça login para editar seu perfil.', 'warning')
        return redirect(url_for('login'))  # Redirecionar para a página de login se não estiver logado

    user_id = session['user_id']
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        password = request.form['password']
        

        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', user=user)

#=====================================================================================#

# Rota para exibir a lista de usuários
@app.route('/users')
def users():
    users = User.query.all()  # Pegando todos os usuários do banco
    return render_template('users.html', users=users)

# Rota para adicionar um novo usuário
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        password = request.form['password']  # Criptografe a senha antes de salvar, se necessário

        new_user = User(username=username, role=role, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Usuário adicionado com sucesso!', 'success')
        return redirect(url_for('users'))
    
    return render_template('add_user.html')  # Formulário de adição de usuário

# Rota para editar um usuário
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.role = request.form['role']
        password = request.form['password']
        if password:
            user.password = password  # Criptografe a senha antes de salvar, se necessário

        db.session.commit()

        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('users'))
    
    return render_template('edit_user.html', user=user)

# Rota para excluir um usuário
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flash('Usuário excluído com sucesso!', 'danger')
    return redirect(url_for('users'))


#=====================================================================================#

# Modelos

class Comanda(db.Model):
    """Modelo de Comandas"""
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default="Aberta")
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    employee = db.relationship('Employee', backref=db.backref('comandas', lazy=True))
    total = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
class ComandaItem(db.Model):
    """Itens adicionados na comanda"""
    id = db.Column(db.Integer, primary_key=True)
    comanda_id = db.Column(db.Integer, db.ForeignKey('comanda.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    comanda = db.relationship('Comanda', backref=db.backref('items', lazy=True))

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Livre')
    value = db.Column(db.Float, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    employee = db.relationship('Employee', backref='rooms', lazy=True)
    timer = db.Column(db.Integer, default=10)  # Tempo estimado em minutos
    checkin_time = db.Column(db.DateTime, nullable=True)  # Horário de início do check-in

class Atendimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)  # ID da garota
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)  # ID do quarto
    entrada = db.Column(db.DateTime, nullable=False)  # Hora de entrada
    saida = db.Column(db.DateTime, nullable=True)  # Hora de saída (opcional)
    tempo = db.Column(db.String(20), nullable=True)  # Tempo total
    valor = db.Column(db.Float, nullable=False)  # Valor cobrado
    observacoes = db.Column(db.Text, nullable=True)  # Observações

    # Relacionamentos
    employee = db.relationship('Employee', backref='atendimentos', lazy=True)
    room = db.relationship('Room', backref='atendimentos', lazy=True)

    def calcular_tempo(self):
        """Calcula o tempo do atendimento em minutos"""
        if self.entrada and self.saida:
            minutos = (self.saida - self.entrada).total_seconds() / 60
            return f"{int(minutos)} min"
        return None


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return f'<Employee {self.name}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # <- Certifique-se de que esta linha está presente
    role = db.Column(db.String(20), nullable=False)


class CashFlow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # Exemplo: "Reservas", "Bar", "Salário"
    description = db.Column(db.String(255), nullable=True)  # Aumentado para descrições detalhadas
    amount = db.Column(db.Float, nullable=False)  # Valor da transação
    date = db.Column(db.DateTime, default=db.func.current_timestamp())  # Data/hora da transação
    type = db.Column(db.String(10), nullable=False)  # "Entrada" ou "Saída"
    payment_method = db.Column(db.String(50), nullable=True)  # Método de pagamento (Dinheiro, Cartão, Pix)
    status = db.Column(db.String(20), default="Pendente")  # "Pendente", "Pago", "Cancelado"
    time = db.Column(db.String(20), nullable=True)  # Tempo do serviço: 30min, 1h, etc.

    # Relacionamentos
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    employee = db.relationship('Employee', backref=db.backref('cashflows', lazy=True))

    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    room = db.relationship('Room', backref=db.backref('room_cashflows', lazy=True))

    atendimento_id = db.Column(db.Integer, db.ForeignKey('atendimento.id'), nullable=True)
    atendimento = db.relationship('Atendimento', backref=db.backref('cashflows', lazy=True))

    def __init__(self, category, description, amount, type, payment_method=None, employee_id=None, room_id=None, atendimento_id=None, time=None, status="Pendente"):
        self.category = category
        self.description = description
        self.amount = amount
        self.type = type
        self.payment_method = payment_method
        self.employee_id = employee_id
        self.room_id = room_id
        self.atendimento_id = atendimento_id
        self.time = time
        self.status = status

    def __repr__(self):
        return f'<CashFlow {self.id} - {self.category} - R$ {self.amount:.2f} ({self.status})>'

# Rotas
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Credenciais inválidas.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    if not username or not password or not role:
        return jsonify({
            "status": "error",
            "title": "Erro no Cadastro",
            "message": "Todos os campos são obrigatórios!",
            "icon": "error"
        }), 400

    if User.query.filter_by(username=username).first():
        return jsonify({
            "status": "error",
            "title": "Usuário já existe",
            "message": f"O nome de usuário '{username}' já está em uso. Tente outro!",
            "icon": "warning"
        }), 400

    new_user = User(username=username, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "status": "success",
        "title": "Cadastro Realizado!",
        "message": f"Usuário '{username}' foi cadastrado com sucesso!",
        "icon": "success"
    }), 200



@app.route('/employees', methods=['GET', 'POST'])
def list_employees():
    if request.method == 'POST':
        # Obtendo os dados do formulário
        name = request.form['name']
        role = request.form['role']
        phone = request.form['phone']  # Adicionando telefone

        # Verificando se os campos obrigatórios foram preenchidos
        if not name or not role or not phone:
            flash('Todos os campos são obrigatórios!', 'danger')
            return redirect(url_for('list_employees'))

        # Criando um novo funcionário
        new_employee = Employee(name=name, role=role, phone=phone)
        try:
            db.session.add(new_employee)
            db.session.commit()
            flash('Funcionário cadastrado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()  # Em caso de erro, faz o rollback
            flash(f'Ocorreu um erro ao cadastrar o funcionário: {str(e)}', 'danger')

        return redirect(url_for('list_employees'))  # Redireciona após cadastro com sucesso

    # Consultando todos os funcionários para exibição
    employees = Employee.query.all()
    return render_template('employees.html', employees=employees)

@app.route('/employees/update/<int:id>', methods=['POST'])
def update_employee(id):
    employee = Employee.query.get(id)
    if employee:
        # Atualizando os dados do funcionário com os dados do formulário
        employee.name = request.form['name']
        employee.role = request.form['role']
        employee.phone = request.form['phone']

        # Commitando a mudança no banco de dados
        db.session.commit()
        return redirect('/employees')  # Redireciona diretamente para a URL '/employees', sem usar 'url_for'

    return "Funcionário não encontrado", 404


@app.route('/employees/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    try:
        db.session.delete(employee)
        db.session.commit()
        flash('Funcionário excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ocorreu um erro ao excluir o funcionário: {str(e)}', 'danger')
    return redirect(url_for('list_employees'))

# Gerenciamento de Quartos

@app.route('/rooms')
def list_rooms():
    now = datetime.now()
    now_minutes = now.hour * 60 + now.minute  # Calcula o tempo total em minutos (exclui segundos)
    rooms = Room.query.all()  # Obtenha todos os quartos
    employees = Employee.query.all()  # Obtenha todos os funcionários

    # Calcula o tempo decorrido para cada quarto (se o check-in já ocorreu)
    for room in rooms:
        if room.checkin_time:  # Verifica se o quarto tem um horário de check-in
            # Verifica o tipo e formato do checkin_time
            if isinstance(room.checkin_time, datetime):
                time_diff = now - room.checkin_time
                room.time_elapsed_minutes = time_diff.total_seconds() / 60  # Converte para minutos
                room.time_elapsed_minutes = round(room.time_elapsed_minutes, 2)  # Arredonda para 2 casas decimais
            else:
                room.time_elapsed_minutes = None  # Se checkin_time não for datetime, define como None
        else:
            room.time_elapsed_minutes = None  # Se não houver check-in, define como None
    
    return render_template('rooms.html', rooms=rooms, now_minutes=now_minutes, employees=employees)


@app.route('/rooms/add', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        name = request.form['name']
        value = float(request.form['value'])
        status = request.form['status']  # Recebendo o status selecionado
        new_room = Room(name=name, value=value, status=status)  # Adicionando o status ao novo quarto
        db.session.add(new_room)
        db.session.commit()
        flash('Quarto adicionado com sucesso!', 'success')
        return redirect(url_for('list_rooms'))
    return render_template('add_room.html')

@app.route('/rooms/checkin/<int:room_id>', methods=['POST'])
def checkin(room_id):
    room = Room.query.get_or_404(room_id)
    
    checkin_time = request.form.get('checkin_time')

    if checkin_time:
        room.timer = int(checkin_time)  # Converte o valor para inteiro (minutos)
    else:
        room.timer = 0  # Se não houver valor, define como 0

    room.checkin_time = datetime.now()  # Armazena o momento exato de check-in

    room.status = "Ocupado"
    
    # Obtém o id do funcionário selecionado
    employee_id = request.form.get('employee_id')
    
    # Verifica se um funcionário foi selecionado
    if employee_id:
        employee = Employee.query.get(employee_id)
        if employee:
            room.employee_id = employee.id  # Associa o funcionário ao quarto
        else:
            return "Funcionário não encontrado", 404
    else:
        return "Funcionário não selecionado", 400
    
    # Salva as mudanças no banco de dados
    db.session.commit()

    # Redireciona para a lista de quartos após o check-in
    return redirect(url_for('list_rooms'))

@app.route('/rooms/alterar_status/<int:room_id>', methods=['POST'])
def alterar_status(room_id):
    room = Room.query.get(room_id)
    if room:
        room.status = 'Livre'  # Alterando o status para 'Livre'
        db.session.commit()
    return redirect(url_for('list_rooms'))  # Redirecionando para a listagem de quartos

@app.route('/rooms/checkout/<int:room_id>', methods=['POST'])
def checkout(room_id):
    room = Room.query.get_or_404(room_id)
    current_time = datetime.now()

    # Verificando se há um check-in registrado
    if not room.checkin_time:
        flash("O quarto não possui um check-in registrado.", "error")
        return redirect(url_for('list_rooms'))

    # Calculando o tempo do atendimento
    time_diff = current_time - room.checkin_time
    time_elapsed_minutes = time_diff.total_seconds() / 60

    # Definindo a categoria de tempo do atendimento
    if time_elapsed_minutes <= 20:
        time_category = "20 minutos"
    elif time_elapsed_minutes <= 30:
        time_category = "30 minutos"
    elif time_elapsed_minutes <= 60:
        time_category = "1 hora"
    elif time_elapsed_minutes <= 90:
        time_category = "1:30 horas"
    elif time_elapsed_minutes <= 120:
        time_category = "2 horas"
    elif time_elapsed_minutes <= 150:
        time_category = "2:30 horas"
    elif time_elapsed_minutes <= 180:
        time_category = "3 horas"
    elif time_elapsed_minutes <= 210:
        time_category = "3:30 horas"
    elif time_elapsed_minutes <= 240:
        time_category = "4 horas"
    else:
        time_category = "+4 horas"

    # Pegando valores do formulário
    try:
        value = float(request.form.get('value', 0))  # Valor do atendimento
        payment_method = request.form.get('payment_method')
        employee_id = request.form.get('employee_id') or room.employee_id
        room_charge = float(request.form.get('room_charge', 0))  # Valor do quarto
        additional_services = float(request.form.get('additional_services', 0))  # Serviços extras

        if not value or not payment_method:
            flash("Todos os campos são obrigatórios!", "error")
            return redirect(url_for('list_rooms'))
    except ValueError:
        flash("Valores inválidos!", "error")
        return redirect(url_for('list_rooms'))

    # Proteção contra duplicação no CashFlow (evita múltiplos registros para o mesmo checkout)
    existing_cashflow = CashFlow.query.filter_by(
        room_id=room_id,
        amount=value,
        description=f"Checkout do quarto {room_id} ({time_category})"
    ).first()

    if existing_cashflow:
        flash("Já existe um registro de checkout para este quarto e valor.", "warning")
        return redirect(url_for('list_rooms'))

    # Atualizando o status do quarto
    room.status = 'Limpeza'
    room.checkout_value = value
    room.payment_method = payment_method
    room.timer = 0
    db.session.commit()

    # Criando o registro no fluxo de caixa para o checkout do quarto
    new_cashflow_room = CashFlow(
        category="Checkout - Quarto",
        description=f"Checkout do quarto {room_id} ({time_category})",
        amount=value,
        type="Entrada",
        employee_id=employee_id,
        room_id=room_id
    )
    db.session.add(new_cashflow_room)

    # Adicionando serviços adicionais ao fluxo de caixa
    if additional_services > 0:
        new_cashflow_services = CashFlow(
            category="Checkout - Serviços Adicionais",
            description=f"Serviços adicionais - Quarto {room_id}",
            amount=additional_services,
            type="Entrada",
            employee_id=employee_id,
            room_id=room_id
        )
        db.session.add(new_cashflow_services)

    # Adicionando comissão do funcionário
    if employee_id:
        new_cashflow_employee = CashFlow(
            category="Comissão Funcionário",
            description=f"Comissão por atendimento no quarto {room_id}",
            amount=value * 0.1,  # 10% de comissão
            type="Saída",
            employee_id=employee_id,
            room_id=room_id
        )
        db.session.add(new_cashflow_employee)

    db.session.commit()

    # Proteção contra duplicação de atendimentos
    existing_atendimento = Atendimento.query.filter_by(
        room_id=room_id,
        entrada=room.checkin_time,
        saida=current_time
    ).first()

    if existing_atendimento:
        flash("Já existe um registro de atendimento para este quarto no mesmo horário.", "warning")
        return redirect(url_for('list_rooms'))

    # Criando o registro do atendimento
    atendimento = Atendimento(
        employee_id=employee_id,  # ID do funcionário (garota)
        room_id=room.id,
        entrada=room.checkin_time,
        saida=current_time,
        tempo=f"{int(time_elapsed_minutes)} min",  # Tempo formatado
        valor=value,
        observacoes=f"Atendimento no quarto {room_id} durante {time_category}",
    )
    db.session.add(atendimento)

    db.session.commit()

    flash("Checkout realizado com sucesso!", "success")
    return redirect(url_for('list_rooms'))


@app.route('/cashflow/delete/<int:cashflow_id>', methods=['POST'])
def delete_cashflow(cashflow_id):
    """Exclui um item do fluxo de caixa"""
    cashflow = CashFlow.query.get_or_404(cashflow_id)

    # Remove o item do banco de dados
    db.session.delete(cashflow)
    db.session.commit()

    flash("Movimentação removida com sucesso!", "success")
    return redirect(url_for('list_cashflow'))


# Gerenciamento de Fluxo de Caixa
@app.route('/cashflow', methods=['GET'])
def list_cashflow():
    """Lista todas as movimentações do fluxo de caixa com a opção de filtro por pesquisa."""
    
    # Obtendo o valor da pesquisa (se houver)
    search = request.args.get('search', '')
    
    # Filtra os registros se houver pesquisa
    if search:
        cashflows = CashFlow.query.filter(
            (CashFlow.employee.has(Employee.name.ilike(f"%{search}%"))) |
            (CashFlow.description.ilike(f"%{search}%")) |
            (CashFlow.room.has(Room.name.ilike(f"%{search}%")))
        ).order_by(CashFlow.date.desc()).all()
    else:
        # Caso não haja pesquisa, traz todas as movimentações
        cashflows = CashFlow.query.order_by(CashFlow.date.desc()).all()
    
    # Calculando o saldo total com base no tipo da movimentação
    total_balance = sum([cf.amount if cf.type == 'Entrada' else -cf.amount for cf in cashflows])
    
    return render_template('cashflow.html', cashflows=cashflows, total_balance=total_balance)


@app.route('/cashflow/add', methods=['POST'])
def add_cashflow():
    """Adiciona uma nova entrada ou saída ao fluxo de caixa."""
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()
    amount = request.form.get('amount', type=float)
    type = request.form.get('type', '').strip()  # Entrada ou Saída
    employee_id = request.form.get('employee_id')  # Opcional
    room_id = request.form.get('room_id')  # Opcional

    # Validação de dados obrigatórios
    if not category or amount is None or not type:
        flash("Erro: Categoria, valor e tipo são obrigatórios.", "danger")
        return redirect(url_for('list_cashflow'))

    try:
        # Converte os IDs para inteiro, se existirem
        employee_id = int(employee_id) if employee_id else None
        room_id = int(room_id) if room_id else None

        # Cria a entrada no fluxo de caixa
        new_cashflow = CashFlow(
            category=category,
            description=description,
            amount=amount,
            type=type,
            employee_id=employee_id,
            room_id=room_id
        )

        # Adiciona e faz o commit
        db.session.add(new_cashflow)
        db.session.commit()

        flash('Movimentação adicionada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()  # Desfaz a transação em caso de erro
        flash(f"Erro ao adicionar movimentação: {str(e)}", "danger")

    return redirect(url_for('list_cashflow'))

# 📌 Rota para exibir a página de atendimentos
@app.route('/atendimentos', methods=['GET'])
def listar_atendimentos():
    atendimentos = Atendimento.query.all()
    employees = Employee.query.all()
    rooms = Room.query.all()
    return render_template('atendimentos.html', atendimentos=atendimentos, employees=employees, rooms=rooms)


# 📌 Rota para buscar todos os atendimentos (JSON)
@app.route('/get_atendimentos', methods=['GET'])
def get_atendimentos():
    atendimentos = Atendimento.query.all()
    atendimentos_data = [
        {
            "id": a.id,
            "garota": a.employee.name if a.employee else "Desconhecida",
            "quarto": a.room.numero if a.room else "N/A",
            "entrada": a.entrada.strftime("%Y-%m-%d %H:%M:%S") if a.entrada else "",
            "saida": a.saida.strftime("%Y-%m-%d %H:%M:%S") if a.saida else "",
            "tempo": a.tempo if a.tempo else "Em andamento",
            "valor": f"R$ {a.valor:.2f}",
            "observacoes": a.observacoes if a.observacoes else "",
        }
        for a in atendimentos
    ]
    return jsonify(atendimentos_data), 200

@app.route('/atendimentos/delete/<int:id>', methods=['POST'])
def excluir_atendimento(id):
    atendimento = Atendimento.query.get(id)
    
    if atendimento:
        db.session.delete(atendimento)  # Remove do banco de dados
        db.session.commit()  # Confirma a remoção
        return jsonify({'message': 'Atendimento removido com sucesso!'}), 200
    
    return jsonify({'error': 'Atendimento não encontrado'}), 404

@app.route('/atendimentos/add', methods=['POST'])
def adicionar_atendimento():
    data = request.json
    employee_id = data['employee_id']
    room_id = data['room_id']
    entrada = datetime.strptime(data['entrada'], '%Y-%m-%d %H:%M:%S')
    saida = datetime.strptime(data['saida'], '%Y-%m-%d %H:%M:%S') if data['saida'] else None
    valor = float(data['valor'])
    observacoes = data['observacoes']

    novo_atendimento = Atendimento(
        employee_id=employee_id,
        room_id=room_id,
        entrada=entrada,
        saida=saida,
        valor=valor,
        observacoes=observacoes
    )

    if saida:
        novo_atendimento.calcular_tempo()

    db.session.add(novo_atendimento)
    db.session.commit()

    # 🔹 Verifica se já existe um registro no CashFlow antes de criar
    if not CashFlow.query.filter_by(atendimento_id=novo_atendimento.id).first():
        novo_fluxo_caixa = CashFlow(
            atendimento_id=novo_atendimento.id,
            categoria="Atendimento",
            descricao=f"Atendimento {novo_atendimento.id}",
            valor=valor,
            data=entrada,
            tipo="Entrada",
            employee_id=employee_id,
            room_id=room_id
        )
        db.session.add(novo_fluxo_caixa)
        db.session.commit()

    return jsonify({'message': 'Atendimento adicionado com sucesso!'}), 201





# 📌 Rota para exibir a página inicial do Bar
@app.route('/index')
def index():
    comandas_abertas = Comanda.query.filter_by(status="Aberta").all()
    return render_template('index.html', comandas=comandas_abertas)

# 📌 Rota para abrir uma comanda
@app.route('/comandas/abrir', methods=['POST'])
def abrir_comanda():
    employee_id = request.form.get('employee_id')
    nova_comanda = Comanda(employee_id=employee_id)
    db.session.add(nova_comanda)
    db.session.commit()
    flash('Comanda aberta com sucesso!', 'success')
    return redirect(url_for('index'))

# 📌 Rota para adicionar um item a uma comanda
@app.route('/comandas/<int:comanda_id>/adicionar', methods=['POST'])
def add_item(comanda_id):
    comanda = Comanda.query.get_or_404(comanda_id)
    if comanda.status != "Aberta":
        flash("Comanda já foi fechada!", "error")
        return redirect(url_for('index'))

    item_id = int(request.form['item_id'])
    quantity = int(request.form['quantity'])
    item = {"id": item_id, "name": "Cerveja", "price": 10.0}  # Exemplo de item fixo

    novo_item = ComandaItem(
        comanda_id=comanda.id,
        name=item["name"],
        price=item["price"],
        quantity=quantity
    )
    comanda.total += item["price"] * quantity
    db.session.add(novo_item)
    db.session.commit()
    flash('Item adicionado!', 'success')

    return redirect(url_for('index'))

# 📌 Rota para fechar uma comanda e registrar no fluxo de caixa
@app.route('/comandas/<int:comanda_id>/fechar', methods=['POST'])
def close_comanda(comanda_id):
    comanda = Comanda.query.get_or_404(comanda_id)
    
    if comanda.status != "Aberta":
        flash("Comanda já foi fechada!", "error")
        return redirect(url_for('index'))

    payment_method = request.form.get('payment_method')
    
    if not payment_method:
        flash("Método de pagamento obrigatório!", "error")
        return redirect(url_for('index'))

    comanda.status = "Fechada"
    db.session.commit()

    # Registrar no fluxo de caixa
    new_cashflow = CashFlow(
        category="Pagamento - Comanda",
        description=f"Pagamento da comanda {comanda.id}",
        amount=comanda.total,
        type="Entrada",
        employee_id=comanda.employee_id,
        comanda_id=comanda.id
    )
    
    db.session.add(new_cashflow)
    db.session.commit()
    
    flash("Comanda fechada e registrada no fluxo de caixa!", "success")
    return redirect(url_for('index'))

# Método principal
if __name__ == '__main__':
    if not os.path.exists('motel.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
