import { render, screen } from '@testing-library/djuno';
import icon from './icon.dj';

describe('Icon Component', () => {
  test('renders with correct icon', () => {
    const { container } = render('<icon_component name="star" />');
    expect(container.querySelector('svg')).toBeInTheDocument();
    expect(container).toMatchSnapshot();
  });
});
