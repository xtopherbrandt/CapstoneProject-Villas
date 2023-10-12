import TextField from '@mui/material/TextField';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterMoment } from '@mui/x-date-pickers/AdapterMoment';
import Stack from '@mui/material/Stack';
import React from 'react';
import { Button } from '@mui/material';
import Box from '@mui/material/Box';
import moment from 'moment';

function postCheckIn(unitNumber, checkInDate, checkOutDate, vehicleLicense, setDirtyFlag ){
    console.log( "Check In" );
    const headers = new Headers();
    headers.append('Authorization', 'Bearer ' + localStorage.getItem('credentials'));
    headers.append('Content-Type', 'application/json');
    const request = new Request("https://api.thesmartcellar.com/checkIn/",
    {
        method: 'POST',
        headers: headers,
        mode:"cors",
        body:JSON.stringify({
          unitNumber: unitNumber,
          checkOutDate:checkOutDate,
          vehicleLicense: vehicleLicense
        })
    });
    
    fetch( request ).then( response => response.json() ).then( (json) => {console.log(json.checkIn); setDirtyFlag(true); });
    
  }
  
  
function CheckIn(props){
    const [checkInDate, setCheckInDate] = React.useState(moment());
    const [checkOutDate, setCheckOutDate] = React.useState(null);
    const [vehicleLicense, setVehicleLicense] = React.useState("");
  
    return(
      <Box sx={{width: '100%', bgcolor: 'background.paper'}}>
        <LocalizationProvider dateAdapter={AdapterMoment}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={{ xs: 1, sm: 2, md: 4}}>
  
  
            <DatePicker
              readOnly
              label="Check In"
              value={checkInDate}
              renderInput={(params) => <TextField {...params} />}
            />
            <DatePicker
              required
              label="Check Out"
              value={checkOutDate}
              onChange={(newValue) => {
                if (newValue >= checkInDate){
                  setCheckOutDate(newValue);
                }
                else{
                  setCheckOutDate(null)
                }
              }}
              renderInput={(params) => <TextField {...params} />}
            />
            <TextField required id="vehicle-license" label="Vehicle License" variant="outlined" value={vehicleLicense} onChange={
              (e) => { setVehicleLicense(e.target.value); }
            }/>
            <Button variant='contained' onClick={() => postCheckIn( props.unitNumber, checkInDate, checkOutDate, vehicleLicense, props.setDirtyFlag )}>Check In</Button>
          </Stack>
        </LocalizationProvider>
      </Box>
      
    );
  }

  export default CheckIn