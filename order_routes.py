from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from models import User, Order
from schemas import OrderModel, OrderStatusModel
from database import Session, engine
from fastapi.encoders import jsonable_encoder

order_router = APIRouter(
    prefix="/order",
    tags=["orders"],
)

session = Session(bind=engine)

@order_router.get("/")
async def hello(Authorize:AuthJWT = Depends()):
    
    """
        ## Sample hello world route
        returns hello world message
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token - {e}"
        )
    return {"message": "Hello, World"}

@order_router.post("/order", status_code=status.HTTP_201_CREATED)
async def place_an_order(order: OrderModel, Authorize:AuthJWT = Depends()):
    """
    # Place order route
    ## Checking user authorization 
    Return reponse in JSON format which represents the order
    
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token - {e}"
        )
    current_user = Authorize.get_jwt_subject()
    user = Session.query(User).filter(User.username == current_user.username).first()

    new_order = Order(
        pizza_size = order.pizza_sizes,
        quantity = order.quantity,
    )

    new_order.user=user
    session.add(new_order)
    session.commit()

    response = {
        "pizza_size": new_order.pizza_sizes,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status": new_order.order_status
    }
    return jsonable_encoder(response)

@order_router.get("/orders")
async def list_all_orders(Authorize:AuthJWT=Depends()):
    """
    # List of all orders
    ## Checking user authorization and checking if user is_staff status is True
    Retrun List of all orders in JSON format or HTTPException if user is not staff
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token - {e}"
        )
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user.username).first()
    if user.is_staff:
        orders = session.query(Order).all()
        return jsonable_encoder(orders)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"User with name {user.username} is not a superuser"
    )

@order_router.get("/orders/{id}")
async def get_order_by_id(id: int, Authorize:AuthJWT = Depends()):
    """
    # Geting order by passing id
    ## Checking user authorization, if user is_staff status is true
    If order exists return target order else return HTTPException
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
         detail=f"Invalid token - {e}"
        )
    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user.username).first()
    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        return jsonable_encoder(order)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not allowed to carry out request"
    )

@order_router.get("/user/orders")
async def get_user_orders(Authorize:AuthJWT = Depends()):
    """
    # Getting all user orders
    ## Checking user authorization
    Return all user orders which have been saved
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
         detail=f"Invalid token - {e}"
        )
    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user.username).first()
    return jsonable_encoder(current_user.orders)

@order_router.get("user/order/{order_id}")
async def get_specific_order(order_id: int, Authorize:AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
         detail=f"Invalid token - {e}"
        )
    subject = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == subject).first()

    orders = current_user.orders
    for order in orders:
        if order.id == order_id:
            return jsonable_encoder(order)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Current user with id {subject.id} have no order with id {order_id}"
    )

@order_router.put("/order/update/{id}")
async def update_order(id: int, order: OrderModel, Authorize:AuthJWT = Depends()):
    """
    # Updating order by passing id
    ## Checking user authorization 
    Return response in JSON format with updated order
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token - {e}"
        )
    order_to_update = session.query(Order).filter(Order.id==id).first()
    order_to_update.quantity = order.quantity
    order_to_update.pizza_sizes = order.pizza_sizes
    order_to_update.flavour = order.flavour

    session.add(order_to_update)
    session.commit()
    response = {
            "id": order.id,
            "quantity": order_to_update.quantity,
            "pizza_sizes": order_to_update.pizza_sizes,
            "order_status": order_to_update.order_status
        }
    return jsonable_encoder(order_to_update)

@order_router.patch("/order/update/{id}")
async def update_order_status(id: int, order: OrderStatusModel, Authorize:AuthJWT = Depends()):
    """
    # Updating order status 
    ## Checking user authorization, if user is_staff status is True 
    Return reponse in JSON format which represents updated order status
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token - {e}"
        )
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user.username).first()
    if user.is_staff:
        status = session.query(Order).filter(Order.id == id).first()
        status.order_status = order.order_status
        session.commit()
        response = {
            "id": order.id,
            "quantity": status.quantity,
            "pizza_sizes": status.pizza_sizes,
            "order_status": status.order_status
        }
        return jsonable_encoder(response)


@order_router.delete("/order/delete/{id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(id: int, Authorize:AuthJWT = Depends()):
    """
    # Deleting an order
    ## Checking user authorization 
    Return response which informs about status code if everything went fine
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token - {e}"
        )
    order_to_delete = session.query(Order).filter(Order.id == id).first()
    session.delete(order_to_delete)
    session.commit()
    return order_to_delete


