var Updatebtn = document.getElementsByClassName('update_cart')

for ( var i=0; i<Updatebtn.length; i++ ){
    Updatebtn[i].addEventListener('click', function(){
        var ProductId = this.dataset.product
        var Action = this.dataset.action

        console.log('productId:',ProductId,'Action:',Action)

        console.log('USER:', user)
        if ( user == 'AnonymousUser' ){
            addCookieItems(ProductId, Action)
        }else{
            updateUserOrder(ProductId,Action)
        }

    })
}

function addCookieItems(ProductId, Action){
    console.log('User Logged out...')

    if(Action == 'add'){
        if(cart[ProductId] == undefined){
            cart[ProductId] = {'quantity':1}
        }else{
            cart[ProductId]['quantity'] += 1

        }

    }

    if(Action == 'remove'){
        cart[ProductId]['quantity'] -= 1

        if(cart[ProductId]['quantity'] <= 0){
            console.log('Item was Deleted')
            delete cart[ProductId]
        }
    }
    
    console.log('cart:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload()
}

function updateUserOrder(ProductId,Action){
    console.log('User is logged in, Retreving the Data..')

    var url = '/update_item/'

    fetch(url, {
        method : 'POST',
        headers : {
            'content-Type':'application/json',
            'X-CSRFToken':csrftoken
        },
        body  : JSON.stringify({'ProductId':ProductId, 'Action':Action})
    })
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        console.log('data:',data)
        location.reload()
    })
}

