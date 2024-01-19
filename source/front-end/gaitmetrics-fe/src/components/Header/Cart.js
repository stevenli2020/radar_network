import React from 'react'
import { Popover, Space, Badge, Empty, Button } from 'antd'
import { DeleteOutlined, ShoppingCartOutlined } from '@ant-design/icons'
import { useSelector, useDispatch } from 'react-redux'

import { remove } from 'reducers/Cart'

const Cart = () => {
  const CartItems = useSelector((state) => state.cart.items)
	const dispatch = useDispatch()
  const CartContent = () => {
    return(
      <>
        {
          CartItems.length > 0 ? CartItems.map((item, index) => (
            <div className='d-flex align-items-center justify-content-between my-3' style={{ minWidth: "300px"}}>
              <div className='me-2'>{item.name}</div>
              <Button 
                danger 
                shape="circle"
                icon={<DeleteOutlined />}
                onClick={() => {
                  dispatch(remove(index))
                }} />
            </div>
          )) : (
            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} style={{ minWidth: "300px"}}/>
          )
        }
      </>
    )
  }

  return (
    <Popover content={CartContent} trigger={'click'} className='me-3'>
      <Space>
        <Badge count={CartItems.length}>
          <ShoppingCartOutlined style={{ fontSize: "30px" }}/>
        </Badge>
      </Space>
    </Popover>
  )
}

export default Cart