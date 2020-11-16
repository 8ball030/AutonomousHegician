import React, { useState } from "react";
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
import Widget from "../../components/Widget/Widget";
const Web3 = require('web3');

const orderPlaceHolderMapping = {
  "0": {},
  "1": {"take_profit_offset_percent": 25},
  "2": {"take_profit_offset_percent": 25},
  "3": {"limit_price": 389.00},
}

class HegicOptions {
  constructor() {
    API.get('get_web3_config')
      .then(results=> results.data)
      .then(results=> {
        this.config = results
        console.log(results);
        this.w3 = new Web3(new Web3.providers.HttpProvider(results.ledger_string))
        this.btc_contract = new this.w3.eth.Contract(results.contract_abis.btcoptions.abi, results.contract_addresses.btcoptions);
        this.eth_contract = new this.w3.eth.Contract(results.contract_abis.ethoptions.abi, results.contract_addresses.ethoptions);
        this.priceprovider = new this.w3.eth.Contract(results.contract_abis.priceprovider.abi, results.contract_addresses.priceprovider);
        this.btcpriceprovider = new this.w3.eth.Contract(results.contract_abis.btcpriceprovider.abi, results.contract_addresses.btcpriceprovider);
        this.estimate_cost("ETH", 60*60*24*2, 1000000, 200, 1 );
        this.latest_answer("ETH" );
      });

  }
  latest_answer(market) {

    return new Promise ((resolve, reject) => {
    if (market === "ETH"){ 
      let contract = this.priceprovider;
          contract.methods.latestAnswer().call(function(err,res){
             if(!err){
                 console.log(res);
                 resolve(res)
             } else {
                 reject(err);
             }
              }  )
        
    }else{
      let contract = this.btcpriceprovider;
          contract.methods.latestAnswer().call(function(err,res){
             if(!err){
                 console.log(res);
                 resolve(res)
             } else {
                 reject(err);
             }
              }  )
        
    }
  })
  };

  estimate_cost(market, period, amount, strike, type) {

    return new Promise ((resolve, reject) => {
    if (market === "ETH"){ 
      let contract = this.eth_contract;
          contract.methods.fees(period, amount, strike, type).call(function(err,res){
             if(!err){
                 console.log(res);
                 resolve(res)
             } else {
                 reject(err);
             }
              }  )
        
    }else{
      let contract = this.btc_contract;
          contract.methods.fees(period, amount, strike, type).call(function(err,res){
             if(!err){
                 console.log(res);
                 resolve(res)
             } else {
                 reject(err);
             }
              }  )
    }
  })
  };
}

const Pricer = new HegicOptions()

export const OptionForm = () => {
  const [state, setState] = useState({
    amount: '400',
    date_created: '',
    date_modified: '',
    execution_strategy_id: -1,
    expiration_date: '',
    fees: '',
    id: '',
    ledger_: '',
    market: 'ETH',
    option_type: '1',
    period: 2,
    status_code_id: '',
    strike_price: '',
    params: {},
    total_cost: 0,
    breakeven: 0,
    latest_answer: 0,
  });
  const [validationErrors, setValidationErrors] = useState({});
  const onChange = name => (e, newValue) => {
    if (!newValue) {
      newValue = e.target.value;
    }
    setState((state) => ({ ...state, [name]: newValue }));
    calc_total_cost()
  }


  async function calc_total_cost() {
    if (isValid()){
      console.log("Ready to Order!");

      const amount = (state.amount* 100000000)
      const price = (state.strike_price * 100000000)
      const period = (state.period * 60 * 60)

      console.log(amount + " " + price + " " + period , state.option_type)
      console.log()


      const fees = await Pricer.estimate_cost(state.market, 
                                        state.period * 60 * 60 * 24, 
                                        amount,
                                        price,
                                        state.option_type
                                        );
                                        
      const latest_price = await Pricer.latest_answer(state.market);
      setState((state) => ({ ...state, ["total_cost"]: fees.total}));
      setState((state) => ({ ...state, ["latest_answer"]: latest_price}));

      const cost_per_unit = (fees.total/amount) * latest_price;
      if (state.option_type == "2"){
        const breakeven = price + cost_per_unit
        console.log("break even " + breakeven + "CAll")
        setState((state) => ({ ...state, ["breakeven"]: breakeven}));
      } else {
        const breakeven = price - cost_per_unit
        console.log("break even " + breakeven + "put")
        setState((state) => ({ ...state, ["breakeven"]: breakeven}));
      }
    }
  }  
  const isValid = () => {
    const validation = {
      strike_price: val => +val > 0,
      amount: val => +val > 0,
      execution_strategy_id: val => +val >= 0,

    };

    let valid = true;
    Object.entries(validation).forEach(([key, val]) => {
      setValidationErrors((state) => ({ ...state, [key]: val(state[key]) }));
      if (!val(state[key])) {
        valid = false;
      }
    });
    return valid
  }
  
  async function sendToAgent() {

    const validation = {
      strike_price: val => +val > 0,
      amount: val => +val > 0,
    };

    let valid = true;
    Object.entries(validation).forEach(([key, val]) => {
      setValidationErrors((state) => ({ ...state, [key]: val(state[key]) }));
      if (!val(state[key])) {
        valid = false;
      }

    });

    if (valid) {
      calc_total_cost();
      console.log("State " +  state.amount);
      
      const amount = (state.amount* 100000000)
      const price = (state.strike_price * 100000000)
      const period = (state.period * 60 * 60)

      const params = {amount: amount,
                      strike_price: price,
                      period: period,
                      breakeven: state.breakeven,
                      option_type: state.option_type,
                      total_cost: state.total_cost,
                      execution_strategy_id: state.execution_strategy_id,
                      market: state.market,
                    }
      const fees = await Pricer.estimate_cost(state.market, 
                                        state.period * 60 * 60 * 24, 
                                        amount,
                                        price,
                                        state.option_type
                                        );
                                        
      const latest_price = await Pricer.latest_answer(state.market);

      const cost_per_unit = (fees.total/amount) * latest_price;

      if (state.option_type == "2"){
        console.log("call!!!")
        params.breakeven = price + cost_per_unit
      } else {
        console.log("put!!!")
        params.breakeven = price - cost_per_unit
      }

      params.total_cost = fees.total
      console.log("params : ");
      console.log(params);

      API.post('create_new_option', {
        headers: {'Content-type': 'application/json'},
        data: params
      });
      API.onload = function () {
          alert("Your option order has successfully been received by the agent.");
          console.log(this.responseText);
      };
      console.log(state)
    }else {
      alert("You Option order is not valid. Please check the parameters")
    }
  }
  return (
    <Widget noBodyPadding style={{ width: "91%" }}>
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        margin: 20,
        padding: 20
      }}
    >
      <div>
      <form style={{ width: "91%" }}>
        <Typography id="discrete-slider" gutterBottom>Market</Typography>
        <FormControl component="fieldset" margin="normal" fullWidth>
          <RadioGroup aria-label="market" error={!validationErrors['market']} onChange={onChange('market')} value={state.market}>
            {['ETH', 'BTC'].map(base => <FormControlLabel value={base} control={<Radio />} label={base} />)}
          </RadioGroup>
        </FormControl>

        <FormControl margin="normal" fullWidth>
          <InputLabel htmlFor="strike">{`Strike Price (${state.market})`}</InputLabel>
          <Input id="strike" type="text" onChange={onChange('strike_price')} error={validationErrors['strike_price']} />
        </FormControl>

        <Typography id="discrete-slider" gutterBottom>
          Period in Days {state.period}
          </Typography>
        <Slider id="period" type="text"
          defaultValue={2}
          name="period"
          aria-labelledby="discrete-slider"
          valueLabelDisplay="auto"
          step={1}
          onChange={onChange('period')}
          min={2}
          max={28}
        />

        <FormControl margin="normal" fullWidth>
          <InputLabel htmlFor="amount">Amount In {state.market}</InputLabel>
          <Input id="amount" type="text" onChange={onChange('amount')} />
        </FormControl>

        <Typography id="discrete-slider" gutterBottom>
          Type of Option
          </Typography>
        <FormControl component="fieldset" name="option_type" margin="normal" fullWidth>
          <RadioGroup aria-label="option_type" name="option_type" onChange={onChange('option_type')}>
            <FormControlLabel value="1" control={<Radio />} label="Put" />
            <FormControlLabel value="2" control={<Radio />} label="Call" />
          </RadioGroup>
        </FormControl>

        <Typography id="discrete-slider" gutterBottom>
          Type of Managed Order
          </Typography>


        <FormControl component="fieldset" margin="normal" fullWidth>
          <RadioGroup aria-label="execution_strategy_id" name="execution_strategy_id" onChange={onChange('execution_strategy_id')}>
            <FormControlLabel value="0" control={<Radio />} label="Auto ITM Closure" />
          </RadioGroup>
        </FormControl>

         {false &&
        <FormControl component="fieldset" margin="normal" fullWidth>
          <RadioGroup aria-label="type_of_order" name="type_of_order" onChange={onChange('type_of_order')} value={state.type_of_order}>
            <FormControlLabel value="0" control={<Radio />} label="Auto ITM Closure" />
            <FormControlLabel value="1" control={<Radio />} label="Take Profit" />
            <FormControlLabel value="2" control={<Radio />} label="Take Profit &amp; Auto ITM Closure" />
            <FormControlLabel value="3" control={<Radio />} label="Limit Order" />
          </RadioGroup>
        </FormControl>
        }

        {false &&
          <FormControl margin="normal" fullWidth>
            <InputLabel htmlFor="params">Take Profit Offset %</InputLabel>
        {['1', '2', '3'].includes(state.execution_strategy_id) && <Input id="params" type="text" onChange={onChange('params')} multiline rows={10} placeholder={orderPlaceHolderMapping[state.execution_strategy_id]}/> }
          </FormControl>
        }

      <br></br>
      <div>
        <h2>Total Cost : </h2>
      <h4>{state.market}: 
      {state.total_cost / 100000000}</h4>
      <h4>${(state.latest_answer * (state.total_cost / 100000000) / 100000000).toFixed(2)}</h4>
      </div>
      <div>
        <h2>Break Even :</h2>
          <h4>${(state.breakeven / 100000000).toFixed(2)}</h4>
      </div>

      <div>
        <Button onClick={sendToAgent} variant="contained" color="primary" size="medium">
          Send to Agent
        </Button>
      </div>
    </form>
    </div>
  </div>
  </Widget>
  );
}

