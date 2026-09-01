import type { ServerUIComponent } from "../types/chat";

import InfoCard from "./server-ui/InfoCard";


interface DynamicRendererProps {
  component: ServerUIComponent;
}


function DynamicRenderer({
  component,
}: DynamicRendererProps) {
  switch (component.type) {
    case "info_card":
      return (
        <InfoCard
          title={component.props.title}
          description={component.props.description}
          rating={component.props.rating}
        />
      );

    case "quick_replies":
      return (
        <div>
          {component.props.options.map((option) => (
            <button
              key={option}
              type="button"
            >
              {option}
            </button>
          ))}
        </div>
      );

    default:
      return null;
  }
}


export default DynamicRenderer;