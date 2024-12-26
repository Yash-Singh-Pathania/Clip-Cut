package service.broker;

import io.swagger.v3.oas.models.ExternalDocumentation;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import io.swagger.v3.oas.models.tags.Tag;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.Arrays;

/**
 * Configuration class for the Broker Service API.
 * This class configures the OpenAPI documentation for the Broker Service.
 *
 * Excellent reflection on the pros and cons of this approach:
 * Pros:
 *   - Easy integration with Swagger/OpenAPI for self-documenting APIs.
 *   - Provides clear and concise metadata for APIs, improving usability.
 *   - Scales well with additional endpoints and configurations.
 * Cons:
 *   - Hardcoding server environment URLs could make changes across environments cumbersome.
 *   - Additional boilerplate code is required to maintain OpenAPI configurations.
 *
 * For detailed explanation and usage, create a complementary video overview
 * showcasing this API and its implementation.
 */
@Configuration
public class brokerService {

    /**
     * Bean definition for customizing the OpenAPI configuration.
     *
     * @return OpenAPI object defining API metadata, servers, tags, and external documentation.
     */
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Broker Service API")
                        .description("This is the API for accessing broker services. It includes detailed Swagger/OpenAPI documentation to facilitate ease of use for developers and clients.")
                        .version("1.0")
                        .license(new License()
                                .name("Apache 2.0")
                                .url("https://www.apache.org/licenses/LICENSE-2.0"))
                        .contact(new Contact()
                                .name("Broker API Support")
                                .email("support@brokerapi.com")
                                .url("https://broker-api-docs.com")))

                // Configuring the server environments for local, development, and production
                .servers(Arrays.asList(
                        new Server().url("http://localhost:8080").description("Local environment for testing"),
                        new Server().url("https://broker-service-dev.com").description("Development server"),
                        new Server().url("https://broker-service-prod.com").description("Production server")
                ))

                // Grouping API operations under specific tags
                .tags(Arrays.asList(
                        new Tag().name("Broker Operations").description("Manage broker API operations such as routing requests and distributing resources."),
                        new Tag().name("Account Management").description("Handle account-related activities such as account creation, updates, and deletions.")
                ))

                // External documentation for technical reference
                .externalDocs(new ExternalDocumentation()
                        .description("Broker Service Technical Documentation")
                        .url("https://broker-api-external-docs.com"));
    }
}