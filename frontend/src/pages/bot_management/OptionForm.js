import React from "react";
import {
  FormControl,
  InputLabel,
  Radio,
  RadioGroup,
  FormControlLabel,
  Input,
  Button,
  Slider,
} from "@material-ui/core";
import Typography from '@material-ui/core/Typography';

import API from '../../api'

class OptionForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {  strike_price: "",
    period: 2,
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
  period_ChangeHandler = (event) => {
    console.log(event.target)
    this.setState({period: event.target.value});
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
    API.post('create_new_option', {
      headers: {'Content-type': 'application/json'},
      data: this.state
    });
    API.onload = function () {
        alert("You new option has been sent to your agent!")
        console.log(this.responseText);
    };
//    API.send(JSON.stringify(this.state));
    console.log("Button Clicked")
  }
  valuetext = (value)  => {
    return value;
  }

  handleChange = (event, value) => this.value = value;

  handleDragStop = () => {
    this.props.update(this.value);
    this.setState({period: this.value});

  }
  onValueChange = (event) => {
    this.setState({
      type_of_option: event.target.value
    });
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
          <h1>Option Creation</h1>

          <FormControl margin="normal" fullWidth>
            <InputLabel htmlFor="strike">Strike Price (ETH/</InputLabel>
            <Input id="strike" type="text" onChange={this.strike_ChangeHandler}/>
          </FormControl>

          <Typography id="discrete-slider" gutterBottom>
             Period in Days 
          </Typography>
          <Slider id="period" type="text" 
                    defaultValue={2}
                    aria-labelledby="discrete-slider"
                    valueLabelDisplay="auto"
                    step={1}
                    onChange={this.handleChange}
                    onDragStop={this.handleDragStop}
                    min={2}
                    max={28}
          />

          <FormControl margin="normal" fullWidth>
            <InputLabel htmlFor="amount">Amount In Ether</InputLabel>
            <Input id="amount" type="text" onChange={this.amount_ChangeHandler}/>
          </FormControl>

          <Typography id="discrete-slider" gutterBottom>
             Type of Option
          </Typography>
          <FormControl component="fieldset" margin="normal" fullWidth>
              <RadioGroup aria-label="type_of_option" name="type_of_option" >
                <FormControlLabel value="put" control={<Radio />} label="Put" onChange={this.onValueChange}/>
                <FormControlLabel value="call" control={<Radio />} label="Call" onChange={this.onValueChange} />
              </RadioGroup>
          </FormControl>


          <Typography id="discrete-slider" gutterBottom>
             Type of Managed Order
          </Typography>

          <FormControl component="fieldset" margin="normal" fullWidth>
              <RadioGroup aria-label="type_of_order" name="type_of_order" onChange={this.type_of_order_ChangeHandler}>
                <FormControlLabel value="0" control={<Radio />} label="Auto ITM Closure" />
              </RadioGroup>
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

export { OptionForm };