const showResponse = () => {
  const result = fetch("http://localhost:5000/gateway/v2");

  result.then(response => {
    response.json().then(data => {
      console.log(data)
    })
  })
}

for (let i = 0; i < 100; i++) {  
  setTimeout(() => {
    showResponse();
  }, 1000 * i);
}
