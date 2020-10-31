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

const orderPlaceHolderMapping = {
  "0": {},
  "1": {"take_profit_offset_percent": 25},
  "2": {"take_profit_offset_percent": 25},
  "3": {"limit_price": 389.00},
}

export const OptionForm = () => {
  const [state, setState] = useState({
    amount: '',
    date_created: '',
    date_modified: '',
    execution_strategy_id: '0',
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
  });
  const [validationErrors, setValidationErrors] = useState({});
  const onChange = name => (e, newValue) => {
    if (!newValue) {
      newValue = e.target.value;
    }
    setState((state) => ({ ...state, [name]: newValue }));
  }
  const sendToAgent = () => {

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
      API.post('create_new_option', {
        headers: {'Content-type': 'application/json'},
        data: state
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
          Period in Days
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
          <InputLabel htmlFor="amount">Amount In Ether</InputLabel>
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
          <RadioGroup aria-label="type_of_order" name="type_of_order" onChange={onChange('type_of_order')}>
            <FormControlLabel value="0" control={<Radio />} label="Auto ITM Closure" />
            <FormControlLabel value="1" control={<Radio />} label="Take Profit" />
            <FormControlLabel value="2" control={<Radio />} label="Take Profit &amp; Auto ITM Closure" />
            <FormControlLabel value="3" control={<Radio />} label="Limit Order" />
          </RadioGroup>
        </FormControl>
        }

        {true &&
          <FormControl margin="normal" fullWidth>
            <InputLabel htmlFor="params">Take Profit Offset %</InputLabel>
        {['1', '2', '3'].includes(state.execution_strategy_id) && <Input id="params" type="text" onChange={onChange('params')} multiline rows={10} placeholder={orderPlaceHolderMapping[state.execution_strategy_id]}/> }
          </FormControl>
        }

        <Button onClick={sendToAgent} variant="contained" color="primary" size="medium">
          Send to Agent
          </Button>
      </form>
    </div>
  );
}

