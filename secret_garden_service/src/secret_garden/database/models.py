from datetime import datetime

from sqlalchemy import (Boolean, Column, Date, DateTime, Float, ForeignKey,
                        Integer, String, UniqueConstraint)
from sqlalchemy.orm import relationship

from src.secret_garden.database.config import Base


class Owner(Base):
    """Modelo de proprietário para o banco de dados"""

    __tablename__ = 'owners'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Nome do proprietário

    # Campos de controle
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.now)

    # Relacionamentos
    clients = relationship('Client', back_populates='owner')

    # Garantir auto incremento no SQLite
    __table_args__ = ({'sqlite_autoincrement': True},)

    def __repr__(self):
        return f"<Owner(id={self.id}, name='{self.name}')>"


class Client(Base):
    """Modelo de cliente para o banco de dados"""

    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String, nullable=False
    )  # Locatário (anteriormente tenant_name)
    owner_id = Column(
        Integer, ForeignKey('owners.id'), nullable=False
    )  # Locador (ID do proprietário)
    status = Column(String, nullable=False)       # Situação
    due_date = Column(Integer, nullable=True)     # Vencimento (dia do mês)

    # Valores financeiros
    amount_paid = Column(Float, nullable=True)    # Valor efetivamente pago
    property_tax = Column(Float, nullable=True)   # IPTU
    interest = Column(Float, nullable=True)       # Juros
    utilities = Column(Float, nullable=True)      # Água/Gás
    insurance = Column(Float, nullable=True)      # Seguro
    condo_fee = Column(Float, nullable=True)      # Condomínio
    percentage = Column(Float, nullable=True)     # %
    delivery_fee = Column(Float, nullable=True)   # Taxa de envio

    # Datas
    start_date = Column(Date, nullable=True)      # Início
    condo_paid = Column(Boolean, default=False)   # Pago condomínio
    withdrawal_date = Column(Date, nullable=True)  # Data ret
    withdrawal_number = Column(String, nullable=True)  # nº ret
    payment_date = Column(Date, nullable=True)    # Data pagamento

    # Outros
    notes = Column(String, nullable=True)         # Observações

    # Campos de controle
    has_monthly_variation = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.now)

    # Relacionamentos
    owner = relationship('Owner', back_populates='clients')
    monthly_calculations = relationship(
        'MonthlyCalculation', back_populates='client'
    )
    payment_returns = relationship('RetornoPagamento', back_populates='client')
    monthly_variable_values = relationship(
        'MonthlyVariableValues', back_populates='client'
    )
    bank_returns = relationship("BankReturn", back_populates="client")

    # Garantir auto incremento no SQLite
    __table_args__ = ({'sqlite_autoincrement': True},)

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}')>"


class MonthlyCalculation(Base):
    """Modelo para armazenar cálculos financeiros mensais dos clientes"""

    __tablename__ = 'monthly_calculations'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    month = Column(Integer, nullable=False)  # Mês (1-12)
    year = Column(Integer, nullable=False)   # Ano (ex: 2023)

    # Valores calculados
    rent_amount = Column(Float, nullable=True)         # Valor do aluguel
    calculation_base = Column(Float, nullable=True)    # Base de cálculo
    tenant_payment = Column(
        Float, nullable=True
    )      # Valor pago pelo locatário
    commission = Column(Float, nullable=True)          # Comissão
    deposit_amount = Column(Float, nullable=True)      # Valor depósito

    # Campos de controle
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.now)

    # Relacionamentos
    client = relationship('Client', back_populates='monthly_calculations')

    # Índice único para evitar duplicação (cliente + mês + ano)
    __table_args__ = (
        # Unique constraint ensures only one calculation per client per month/year
        {'sqlite_autoincrement': True},
    )

    def __repr__(self):
        return f"<MonthlyCalculation(id={self.id}, client_id={self.client_id}, month={self.month}, year={self.year})>"


class RetornoPagamento(Base):
    """Modelo para armazenar informações de retorno de pagamentos"""
    __tablename__ = "retornos_pagamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    month = Column(Integer, nullable=False)  # Mês (1-12)
    year = Column(Integer, nullable=False)   # Ano (ex: 2023)
    
    # Informações do boleto/pagamento
    due_date = Column(Date, nullable=False)          # Data de vencimento
    payment_date = Column(Date, nullable=False)      # Data de pagamento
    rent_amount = Column(Float, nullable=False)      # Valor do aluguel (título)
    amount_paid = Column(Float, nullable=False)      # Valor efetivamente pago
    
    # Valores financeiros
    interest = Column(Float, default=0.0)            # Juros
    condo_fee = Column(Float, default=0.0)           # Condomínio
    percentage = Column(Float, default=0.0)          # Percentual
    commission = Column(Float, default=0.0)          # Comissão
    delivery_fee = Column(Float, default=0.0)        # Taxa de envio
    condo_paid = Column(Boolean, default=False)      # Pago condomínio
    owner_payment_amount = Column(Float, default=0.0) # Valor a pagar ao proprietário
    
    # Campos de controle
    processed_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relacionamentos
    client = relationship("Client", back_populates="payment_returns")
    
    # Índice único para evitar duplicação (cliente + mês + ano)
    __table_args__ = (
        # Unique constraint ensures only one return per client per month/year
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self):
        return f"<RetornoPagamento(id={self.id}, client_id={self.client_id}, month={self.month}, year={self.year})>"


class MonthlyVariableValues(Base):
    """Modelo para armazenar valores que podem variar mensalmente"""
    __tablename__ = 'monthly_variable_values'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    month = Column(Integer, nullable=False)  # Mês (1-12)
    year = Column(Integer, nullable=False)   # Ano (ex: 2023)

    # Valores que podem variar mensalmente
    water_bill = Column(Float, nullable=True)        # Conta de água
    gas_bill = Column(Float, nullable=True)          # Conta de gás
    insurance = Column(Float, nullable=True)         # Seguro
    property_tax = Column(Float, nullable=True)      # IPTU
    condo_fee = Column(Float, nullable=True)         # Condomínio
    condo_paid_by_agency = Column(Boolean, default=False)  # Condomínio pago pela imobiliária

    # Campos de controle
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.now)

    # Relacionamentos
    client = relationship('Client', back_populates='monthly_variable_values')

    # Índice único para evitar duplicação (cliente + mês + ano)
    __table_args__ = (
        UniqueConstraint('client_id', 'month', 'year', name='uix_client_month_year'),
    )

    def __repr__(self):
        return f"<MonthlyVariableValues(id={self.id}, client_id={self.client_id}, month={self.month}, year={self.year})>"


class BankReturn(Base):
    """Modelo para retornos bancários"""
    __tablename__ = 'bank_returns'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    payer_name = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
    payment_date = Column(Date, nullable=True)
    title_amount = Column(Float, nullable=True)  # Valor do título
    charged_amount = Column(Float, nullable=True)  # Valor cobrado
    variation_amount = Column(Float, nullable=True)  # Valor da oscilação
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    # Relacionamentos
    client = relationship("Client", back_populates="bank_returns")

    # Garantir que só exista um registro por cliente/mês/ano
    __table_args__ = (
        UniqueConstraint('client_id', 'month', 'year', name='uix_bank_return_client_month_year'),
    )

    def __repr__(self):
        return f"<BankReturn(id={self.id}, client_id={self.client_id}, month={self.month}, year={self.year})>"
