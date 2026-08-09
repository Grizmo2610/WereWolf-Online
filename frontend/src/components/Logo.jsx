import logo from '../assets/images/Werewolf-logo.png'

export default function Logo({ className = 'h-16 w-16' }) {
  return <img src={logo} alt="Ma Sói Online" className={`${className} object-contain`} />
}
