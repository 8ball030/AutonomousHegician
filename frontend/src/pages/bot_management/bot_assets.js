import React  from 'react';
import { makeStyles } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Button from '@material-ui/core/Button';

import Highcharts from 'highcharts';
import {
  HighchartsChart, Chart, withHighcharts, XAxis, YAxis, Title, Legend, ColumnSeries, SplineSeries, PieSeries
} from 'react-jsx-highcharts';
const plotOptions = {
  series: {
    pointStart: 2020
  }
};
const useStyles = makeStyles((theme) => ({
  button: {
    display: 'block',
    marginTop: theme.spacing(2),
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 120,
  },
}));


var selected_key = "";

function ControlledOpenSelect(agent_data) {
  const data = agent_data;
  const classes = useStyles();
  const [age, setAge] = React.useState('');
  const [open, setOpen] = React.useState(false);

  const handleChange = (event) => {
    setAge(event.target.value);
    selected_key = age;
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleOpen = () => {
    setOpen(true);
  };

  return (
    <div>
      <Button className={classes.button} onClick={handleOpen}>
        Open the select
      </Button>
      <FormControl className={classes.formControl}>
        <InputLabel id="demo-controlled-open-select-label">Age</InputLabel>
        <Select
          labelId="demo-controlled-open-select-label"
          id="demo-controlled-open-select"
          open={open}
          onClose={handleClose}
          onOpen={handleOpen}
          value={age}
          onChange={handleChange}
        >
          <MenuItem value="">
            <em>None</em>
          </MenuItem>
          {Object.values(data.agent_data).map((keyName, i) => (
              console.log(keyName.id),
              <MenuItem key={keyName.id} value={keyName.id}>{keyName.name}</MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>
  );
}



const agent_data =[{'coin': 'USDT', 'free': 0.0, 'total': 0.0, 'usdValue': 2.5031455e-09},
 {'coin': 'BTC',
  'free': 0.08552497,
  'total': 0.11043491,
  'usdValue': 1302.8794711600162},
 {'coin': 'BEAR', 'free': 0.0, 'total': 0.0, 'usdValue': 0.0},
 {'coin': 'PAXG', 'free': 0.0, 'total': 0.0, 'usdValue': 0.0},
 {'coin': 'USD',
  'free': 7.68805447,
  'total': 7.68805447,
  'usdValue': 7.688054475573361},
 {'coin': 'ETH', 'free': 0.0, 'total': 0.0, 'usdValue': 0.0}]

const Assets= ({data}) => (
  <div className="bot_assets">
  <div>
    <ControlledOpenSelect agent_data={data}/>
  </div>
    <HighchartsChart plotOptions={plotOptions}>
        <Chart />

    <Title>Holdings Over Time</Title>

    <Legend />

    <XAxis categories={['Apples', 'Oranges', 'Pears', 'Bananas', 'Plums']} />

    <YAxis>
      <ColumnSeries name="BTC" data={data} />
      <ColumnSeries name="PAXG" data={[2, 3, 5, 7, 6]} />
      <ColumnSeries name="USD" data={[4, 3, 3, 9, 0]} />
      <SplineSeries name="Average" data={[3, 2.67, 3, 6.33, 3.33]} />
      <PieSeries name="Total consumption" data={agent_data} center={[100, 80]} size={100} showInLegend={false} />
    </YAxis>
  
  
    </HighchartsChart>
  </div>
);

export default withHighcharts(Assets, Highcharts);
