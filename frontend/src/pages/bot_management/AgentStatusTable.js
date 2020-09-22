import React from "react";
import {
  FormControl,
  InputLabel,
  FormLabel,
  Radio,
  RadioGroup,
  FormControlLabel,
  Input,
  Button,
  TextField,
  Typography,
} from "@material-ui/core";

class Contact extends React.Component {
  constructor(props) {
    super(props);
    this.state = {  strike_price: "",
    expiration_date: "",
    amount: "",
    type_of_option: "",
    type_of_order: "",
    status: "",
    optionID: "",
    params: {}
  }
    
  }
  strike_ChangeHandler = (event) => {
    console.log(event.target)
    this.setState({strike_price: Number(event.target.value)});
  }
  expiration_ChangeHandler = (event) => {
    console.log(event.target)
    this.setState({expiration_date: event.target.value});
  }
  amount_ChangeHandler = (event) => {
    console.log(event.target)
    this.setState({amount: Number(event.target.value)});
  }

  type_of_option_ChangeHandler = (event) => {
    console.log(event.target)
    this.setState({type_of_option: event.target.value});
  }
  type_of_order_ChangeHandler = (event) => {
    console.log(event.target)
    this.setState({type_of_order: event.target.value});
  }
  status_ChangeHandler = (event) => {
    console.log(event.target)
    this.setState({status: event.target.value});
  }

  optionID_ChangeHandler = (event) => {
    console.log(event.target)
    this.setState({optionID: Number(event.target.value)});
  }

  params_ChangeHandler = (event) => {
    console.log(event.target)
    this.setState({params: event.target.value});
  }

  sendToAgent = () => {
    console.log(this.state)
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://localhost:8080/create_new_option', true);
    xhr.setRequestHeader('Content-type', 'application/json');
    xhr.onload = function () {
        alert("You new option has been sent to your agent!")
        console.log(this.responseText);
    };
    xhr.send(JSON.stringify(this.state));
    console.log("Btoon Clicked")
  }

  render() {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          margin: 20,
          padding: 20
        }}
      >
        <form style={{ width: "50%" }}>
          <Typography variant="h2">Contract Management</Typography>

          <FormControl margin="normal" fullWidth>
            <InputLabel htmlFor="optionID">Option Id</InputLabel>
            <Input id="optionID" type="text" onChange={this.optionID_ChangeHandler}/>
          </FormControl>

          <FormControl margin="normal" fullWidth>
            <InputLabel htmlFor="strike">Strike Price</InputLabel>
            <Input id="strike" type="text" onChange={this.strike_ChangeHandler}/>
          </FormControl>

          <FormControl margin="normal" fullWidth>
            <InputLabel htmlFor="expiration">Expiration Date</InputLabel>
            <Input id="expiration" type="text" onChange={this.expiration_ChangeHandler}/>
          </FormControl>

          <FormControl margin="normal" fullWidth>
            <InputLabel htmlFor="amount">Amount</InputLabel>
            <Input id="amount" type="text" onChange={this.amount_ChangeHandler}/>
          </FormControl>

          <FormControl margin="normal" fullWidth>
            <InputLabel htmlFor="type_of_option">Type Of Option</InputLabel>
            <Input id="type_of_option" type="text" onChange={this.type_of_option_ChangeHandler}/>
          </FormControl>

          <FormControl margin="normal" fullWidth>
            <InputLabel htmlFor="type_of_order">Type Of Order</InputLabel>
            <Input id="type_of_order" type="text" onChange={this.type_of_order_ChangeHandler}/>
          </FormControl>

          <FormControl margin="normal" fullWidth>
            <InputLabel htmlFor="status">Order Status</InputLabel>
            <Input id="status" type="text" onChange={this.status_ChangeHandler}/>
          </FormControl>

          <FormControl margin="normal" fullWidth>
            <InputLabel htmlFor="params">Order Parameters</InputLabel>
            <Input id="params" type="text" onChange={this.params_ChangeHandler} multiline rows={10}/>
          </FormControl>

          <Button onClick={this.sendToAgent} variant="contained" color="primary" size="medium">
            Send to Agent
          </Button>
        </form>
      </div>
    );
  }
}

export default Contact;