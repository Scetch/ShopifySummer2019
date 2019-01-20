from functools import reduce

import graphene
from graphene import resolve_only_args
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphql_relay import from_global_id

import models
from models import db_session

class Product(SQLAlchemyObjectType):
    class Meta:
        model = models.Product
        interfaces = (graphene.relay.Node, )

class ProductConnection(graphene.relay.Connection):
    class Meta:
        node = Product

class CartItem(SQLAlchemyObjectType):
    class Meta:
        model = models.CartItem
        interfaces = (graphene.relay.Node, )

class Cart(SQLAlchemyObjectType):
    class Meta:
        model = models.Cart
        interfaces = (graphene.relay.Node, )

    total = graphene.Field(graphene.Float, description='The total amount of money the cart is worth')

    def resolve_total(self, info):
        # For every item in the cart, multiply the item quantity by the product price it is assigned to
        # and then sum
        return reduce(lambda acc, item: acc + (item.quantity * item.product.price), self.items, 0.0)

class CartConnection(graphene.relay.Connection):
    class Meta:
        node = Cart

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()

    cart = graphene.relay.Node.Field(Cart, description='Get an individual cart by id')
    carts = SQLAlchemyConnectionField(CartConnection, description='Get a list of all carts')
    product = graphene.relay.Node.Field(Product, description='Get an individual product by id')
    products = SQLAlchemyConnectionField(ProductConnection, description='Get a list of all products')
    availableProducts = graphene.List(Product, description='Get a list of available carts')

    def resolve_availableProducts(self, info):
        # Query the database fr all products that have available inventory
        return Product.get_query(info).filter(models.Product.inventory_count > 0).all()

class CreateCart(graphene.Mutation):
    Output = Cart

    @classmethod
    def mutate(cls, _, info, **args):
        #  Add a new Cart to the database
        c = models.Cart()
        db_session.add(c)
        db_session.commit()
        return c

class AddProductToCart(graphene.Mutation):
    class Arguments:
        productId = graphene.ID(required=True)
        cartId = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    Output = Cart

    @classmethod
    def mutate(cls, _, info, **args):
        # Convert the productId and cartId from global ids to database ids
        productId = from_global_id(args.get('productId'))[1]
        cartId = from_global_id(args.get('cartId'))[1]
        quantity = args.get('quantity')
        
        if quantity < 0:
            raise Exception('Quantity must be > 0')

        product = Product.get_query(info).get(productId)
        if product is None:
            raise Exception('Invalid productId')

        cart = Cart.get_query(info).get(cartId)
        if cart is None:
            raise Exception('Invalid cartId')

        item = CartItem.get_query(info).filter(models.CartItem.cart_id == cartId and models.CartItem.product_id == product_id).first()
        if item is None:
            item = models.CartItem(product_id=productId, cart_id=cartId, quantity=quantity)
            db_session.add(item)
        else:
            item.quantity += quantity

        db_session.commit()

        return cart

class DeleteProductFromCart(graphene.Mutation):
    class Arguments:
        productId = graphene.ID(required=True)
        cartId = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    Output = Cart

    @classmethod
    def mutate(cls, _, info, **args):
        # Convert the productId and cartId from global ids to database ids
        productId = from_global_id(args.get('productId'))[1]
        cartId = from_global_id(args.get('cartId'))[1]
        quantity = args.get('quantity')

        if quantity < 0:
            raise Exception('Quantity must be > 0')

        product = Product.get_query(info).get(productId)
        if product is None:
            raise Exception('Invalid productId')

        cart = Cart.get_query(info).get(cartId)
        if cart is None:
            raise Exception('Invalid cartId')

        item = CartItem.get_query(info).filter(models.CartItem.cart_id == cartId and models.CartItem.product_id == product_id).first()
        if item is None:
            raise Exception('Trying to remove a product when it did not exist in the first place.')
        else:
            if item.quantity - quantity <= 0:
                db_session.delete(item)
            else:
                item.quantity -= quantity
        
        db_session.commit()

        return cart

class CompleteCart(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    Output = Cart

    @classmethod
    def mutate(cls, _, info, **args):
         # Convert the cartId from global ids to database ids
        id = from_global_id(args.get('id'))[1]
        cart = Cart.get_query(info).filter(models.Cart.id == id).first()
        if not cart:
            raise Exception('Invalid cart')

        if cart.completed:
            raise Exception('Cart is already completed')

        # For each item in the cart, check if the quantity of the item is more than the inventory available
        # and if it is raise an exception
        # If it's not subtract the quantity from available inventory
        for item in cart.items:
            if item.quantity > item.product.inventory_count:
                raise Exception('Item quantity is larger than product inventory')
            
            item.product.inventory_count -= item.quantity

        cart.completed = True

        db_session.commit()
        
        return cart

class Mutations(graphene.ObjectType):
    createCart = CreateCart.Field(description='Create a new cart')
    addProductToCart = AddProductToCart.Field(description='Add a product to a cart')
    deleteProductFromCart = DeleteProductFromCart.Field(description='Delete a product from a cart')
    completeCart = CompleteCart.Field(description='Complete the cart')

schema = graphene.Schema(query=Query, mutation=Mutations)