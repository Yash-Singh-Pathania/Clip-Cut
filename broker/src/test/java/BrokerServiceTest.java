import io.swagger.v3.oas.models.ExternalDocumentation;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.servers.Server;
import io.swagger.v3.oas.models.tags.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import service.broker.brokerService;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

@SpringBootTest(classes = brokerService.class) // Specify the config class
public class BrokerServiceTest {

    @Autowired
    private OpenAPI openAPI;

    @Test
    public void testOpenAPIBeanCreation() {
        // Validate the OpenAPI info section
        Info info = openAPI.getInfo();
        assertNotNull(info);
        assertEquals("Broker Service API", info.getTitle());
        assertEquals("1.0", info.getVersion());
        assertEquals("This is the API for accessing broker services.", info.getDescription());
        assertNotNull(info.getLicense());
        assertEquals("Apache 2.0", info.getLicense().getName());
        assertEquals("https://www.apache.org/licenses/LICENSE-2.0", info.getLicense().getUrl());

        // Validate contact information
        Contact contact = info.getContact();
        assertNotNull(contact);
        assertEquals("Broker API Support", contact.getName());
        assertEquals("support@brokerapi.com", contact.getEmail());
        assertEquals("https://broker-api-docs.com", contact.getUrl());

        // Validate server URLs
        List<Server> servers = openAPI.getServers();
        assertNotNull(servers);
        assertEquals(3, servers.size());
        assertEquals("http://localhost:8080", servers.get(0).getUrl());
        assertEquals("https://broker-service-dev.com", servers.get(1).getUrl());
        assertEquals("https://broker-service-prod.com", servers.get(2).getUrl());

        // Validate tags
        List<Tag> tags = openAPI.getTags();
        assertNotNull(tags);
        assertEquals("Broker Operations", tags.get(0).getName());
        assertEquals("Manage broker API operations", tags.get(0).getDescription());
        assertEquals("Account Management", tags.get(1).getName());
        assertEquals("Handle account-related activities", tags.get(1).getDescription());

        // Validate external documentation
        ExternalDocumentation externalDocs = openAPI.getExternalDocs();
        assertNotNull(externalDocs);
        assertEquals("Broker Service Technical Documentation", externalDocs.getDescription());
        assertEquals("https://broker-api-external-docs.com", externalDocs.getUrl());
    }
}