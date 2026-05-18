import { Routes, Route } from 'react-router-dom';

import Homepage from './Pages/homepage';
import Albapage from './Pages/albapage';

function App() {
	return (
		<div className="app-container">
			<Routes>
				<Route path="/" element={<Homepage />} />
				<Route path="/alba" element={<Albapage />} />
			</Routes>
		</div>
	);
}

export default App;